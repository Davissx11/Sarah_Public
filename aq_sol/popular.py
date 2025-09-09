from collections.abc import Generator, Iterable
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from itertools import islice
from logging import CRITICAL, ERROR, Logger, getLogger
from pathlib import Path
from time import sleep
from zoneinfo import ZoneInfo

import requests
from sqlalchemy import Column, DateTime, Integer, String, create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from wikipedia import get_page
from wikipedia.exceptions import DisambiguationError, PageError

from aq_sol.eda import TMP

CONTACT_URL = "https://sector6.net/jhanley741/wiki-contact.html"


@contextmanager
def suppress_warnings(log: Logger, level: int = ERROR) -> Generator[None]:
    """Temporarily set the logger to a specified level."""
    original_level = log.level
    try:
        log.setLevel(level)
        yield
    finally:
        log.setLevel(original_level)


@contextmanager
def suppress_errors(log: Logger, level: int = CRITICAL) -> Generator[None]:
    """Temporarily set the logger to a specified level."""
    original_level = log.level
    try:
        log.setLevel(level)
        yield
    finally:
        log.setLevel(original_level)


def _ymd(d: datetime) -> str:
    return d.strftime("%Y%m%d")


_punct_to_slash = str.maketrans(
    "/,;[()]~",
    "////////",
)


def _has_punctuation(s: str) -> bool:
    return "/" in s.translate(_punct_to_slash)
    # Examples of input names that contain punctuation:
    # - Atovaquone(0,430mg/ml) - neutral
    # - Benzenamine,_N-Phenyl-,_Styrenated
    # - Aluminum;phosphenic acid
    # - Anthra[2,1,9-mna]naphtho[2,3-h]acridine-
    # - Benzyl_Phenyl(Sulfooxy)Acetate


def _rate_limit_sleep(brief_pause: float = 0.1) -> None:
    """Avoid hammering the wiki servers, or they'll ban our client IP."""
    sleep(brief_pause)


def get_pageviews(title: str, days: int = 30) -> int:
    headers = {
        "accept": "application/json",
        "user-agent": CONTACT_URL,
    }
    tz = ZoneInfo("America/Los_Angeles")
    end_date = datetime.now(tz=tz)
    start_date = end_date - timedelta(days=days)
    base_url = (
        "https://wikimedia.org/api/rest_v1/metrics/"
        "pageviews/per-article/en.wikipedia.org/all-access/user"
    )
    url = f"{base_url}/{title}/daily/{_ymd(start_date)}/{_ymd(end_date)}"
    # e.g. .../Potassium_chloride/daily/20250801/20250831

    resp = requests.get(url, headers=headers)
    if resp.status_code == 404:
        # https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/
        # en.wikipedia.org/all-access/user/formaldehyde_resin/daily/20250808/20250907
        return 0
    resp.raise_for_status()
    d = resp.json()
    items = d["items"]
    return sum(item["views"] for item in items)


def popularity(chem: str) -> tuple[str, int]:

    log = getLogger("wikipedia.wikipedia")
    with suppress_warnings(log):  # no "redirect" chatter
        pg = get_page(chem)
    title = Path(pg.url).name
    # example mismatch: 'Acetyl_Sulfisoxazole', 'Sulfafurazole'
    # assert chem == title, (chem, title)

    return title, get_pageviews(chem)


def now() -> datetime:
    return datetime.now(UTC).replace(second=0, microsecond=0)


class Base(DeclarativeBase): ...


class CName(Base):
    __tablename__ = "cname"  # canonical name, in wikipedia
    name = Column(String, primary_key=True)
    cname = Column(String, nullable=False)
    modified = Column(DateTime, nullable=False, default=now)


class PView(Base):
    __tablename__ = "pview"
    cname = Column(String, primary_key=True)
    page_views = Column(Integer, nullable=False)
    modified = Column(DateTime, nullable=False, default=now)

    def __repr__(self) -> str:
        return f"<Cache(cname='{self.cname}', page_views={self.page_views})>"


class PopCache:
    DB_FILE = TMP / "wiki_cache.sqlite"

    def __init__(self) -> None:
        engine = create_engine(f"sqlite:///{self.DB_FILE}", isolation_level="AUTOCOMMIT")
        Base.metadata.create_all(engine)
        self.conn = engine.connect()

    def close(self) -> None:
        self.conn.commit()
        self.conn.close()

    def get_session(self) -> Session:
        return sessionmaker(bind=self.conn)()

    def exists(self, name: str) -> bool:
        select = text("SELECT 1 FROM cname WHERE name = :name")
        result = self.conn.execute(select, {"name": name})
        return bool(result.fetchone())

    def add_names(self, names: Iterable[str]) -> None:
        log = getLogger("wikipedia.wikipedia")

        # Post Conditions
        # PC 1: name will exist in the cname table, pointing at NULL or a cname
        # PC 2: If cname is non NULL, the pview.page_views column will be positive.
        with self.get_session() as sess:
            for name in islice(names, 10_000):
                # name = "Sulfafurazole"  # from Acetyl_Sulfisoxazole
                if _has_punctuation(name):
                    continue

                q_c = sess.query(CName).filter_by(name=name)
                if first := q_c.first():
                    if not f"{first.cname}":
                        continue
                else:
                    # Go look up the cannonical name.
                    _rate_limit_sleep()
                    insert = CName(name=name, cname="")  # Make a note that there _is_ no cname.
                    with suppress_errors(log):  # no "redirect" chatter
                        try:
                            pg = get_page(name)
                            cname = Path(pg.url).name
                            insert = CName(name=name, cname=cname)
                        except PageError:
                            # Page id "FOO" does not match any pages. Try another id!
                            continue
                        except DisambiguationError as e:
                            assert '" may refer to:' in f"{e}", e
                            continue
                        except ValueError as e:
                            assert "Either a title or a pageid must be specified" in f"{e}"
                            continue  # Page id "Calcoloid_Olive_R" does not match any pages
                        except KeyError as e:
                            print(f"key error on {name}: {e} .")
                            assert f"{e}" == "'fullurl'", f"{e}"
                            continue
                        finally:
                            sess.add(insert)
                            sess.commit()

                q_c = sess.query(CName).filter_by(name=name)
                cname_entry = q_c.first()
                assert cname_entry
                cname = f"{cname_entry.cname}"

                q_pv = sess.query(PView).filter_by(cname=cname)
                if not q_pv.first():
                    _rate_limit_sleep()
                    pv = get_pageviews(cname)
                    print(f"{name:<20} --> {pv:6d}   {cname}")
                    row = PView(cname=cname, page_views=pv)
                    sess.add(row)
                    sess.commit()
            sess.commit()
