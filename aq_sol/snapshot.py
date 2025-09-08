#! /usr/bin/env YDATA_SUPPRESS_BANNER=1 python

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


if __name__ == "__main__":
    write_wiki_snapshot()
