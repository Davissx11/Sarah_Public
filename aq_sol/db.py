from pathlib import Path

import numpy as np
from sqlalchemy import Engine, create_engine, text

from aq_sol.eda import TMP, get_solubility_df

DB_FILE = TMP / "aq_sol.sqlite"


def get_engine(db_file: Path = DB_FILE) -> Engine:
    return create_engine(f"sqlite:///{db_file}", isolation_level="AUTOCOMMIT")


def create_aq_sol_table(table_name: str = "aq_sol") -> str:
    with get_engine().connect() as conn:
        drop = text(f"DROP TABLE  IF EXISTS  {table_name}")
        conn.execute(drop)

        df = get_solubility_df()
        df["ocurrences"] = df.ocurrences.astype(np.int32)

        df.to_sql(table_name, conn, index=False)
        return table_name
