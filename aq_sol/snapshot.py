#! /usr/bin/env YDATA_SUPPRESS_BANNER=1 python

"""
To refresh RDBMS from *.csv files:
    $ rm /tmp/wiki_cache.sqlite; aq_sol/snapshot.py
"""

from pathlib import Path

import pandas as pd
from sqlalchemy import text

from aq_sol.popular import PopCache

REPO_TOP = Path(__file__ + "/../..").resolve()
OUT = REPO_TOP / "aq_sol/out"


def write_wiki_snapshot() -> None:
    for table, order in [
        ("cname", "name"),
        ("pview", "page_views DESC, cname"),
    ]:
        select = f"SELECT *  FROM {table}  ORDER BY {order}"
        df = pd.read_sql(text(select), PopCache().conn)
        df.to_csv(OUT / f"{table}.csv", index=False)


def load_tables_if_empty() -> None:
    pc = PopCache()
    select = "SELECT COUNT(*)  FROM pview"
    with pc.get_session() as sess:
        row = sess.execute(text(select)).first()
        assert row
    (n,) = row
    if int(n) == 0:
        df_c = pd.read_csv(OUT / "cname.csv")
        df_c["cname"] = df_c.cname.replace({None: ""})
        df_c.to_sql("cname", pc.conn, if_exists="append", index=False)

        df_pv = pd.read_csv(OUT / "pview.csv")
        df_pv.to_sql("pview", pc.conn, if_exists="append", index=False)


if __name__ == "__main__":
    load_tables_if_empty()
    write_wiki_snapshot()
