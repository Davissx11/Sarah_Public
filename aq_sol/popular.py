import datetime as dt
from collections.abc import Generator, Iterable
from contextlib import contextmanager
from datetime import timedelta
from logging import ERROR, Logger, getLogger
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from sqlalchemy import Column, Integer, String, create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from wikipedia import get_page

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


def _ymd(d: dt.datetime) -> str:
    return d.strftime("%Y%m%d")


def get_pageviews(title: str, days: int = 30) -> int:
    headers = {
        "accept": "application/json",
        "user-agent": CONTACT_URL,
    }
    tz = ZoneInfo("America/Los_Angeles")
    end_date = dt.datetime.now(tz=tz)
    start_date = end_date - timedelta(days=days)
    base_url = (
        "https://wikimedia.org/api/rest_v1/metrics/"
        "pageviews/per-article/en.wikipedia.org/all-access/user"
    )
    url = f"{base_url}/{title}/daily/{_ymd(start_date)}/{_ymd(end_date)}"
    # e.g. .../Potassium_chloride/daily/20250801/20250831

    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    d = resp.json()
    items = d["items"]
    return sum(item["views"] for item in items)


def popular(chem: str) -> int:

    log = getLogger("wikipedia.wikipedia")
    with suppress_warnings(log):  # no "redirect" chatter
        pg = get_page(chem)
    assert " " in f"{pg.title}"
    title = Path(pg.url).name
    assert title == chem

    return get_pageviews(chem)


class Base(DeclarativeBase): ...


class Cache(Base):
    __tablename__ = "cache"
    name = Column(String, primary_key=True)
    page_views = Column(Integer)

    def __repr__(self) -> str:
        return f"<Cache(name='{self.name}', page_views={self.page_views})>"


class PopCache:
    DB_FILE = TMP / "wiki_cache.sqlite"

    def __init__(self) -> None:
        engine = create_engine(f"sqlite:///{self.DB_FILE}", isolation_level="AUTOCOMMIT")
        self.conn = engine.connect()

    def close(self) -> None:
        self.conn.commit()
        self.conn.close()

    def get_session(self) -> Session:
        return sessionmaker(bind=self.conn)()

    def exists(self, name: str) -> bool:
        select = text("SELECT 1 FROM cache WHERE name = :name")
        result = self.conn.execute(select, {"name": name})
        return bool(result.fetchone())

    def add_names(self, names: Iterable[str], page_views: int) -> None:
        with self.get_session() as sess:
            for name in sorted(names):
                if not self.exists(name):
                    row = Cache(name=name, page_views=page_views)
                    sess.add(row)
            sess.commit()
