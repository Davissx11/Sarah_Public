from pathlib import Path

import numpy as np
from sqlalchemy import Engine, MetaData, Table, create_engine, func, select, text
from sqlalchemy.orm import sessionmaker

from aq_sol.eda import TMP, get_solubility_df

DB_FILE = TMP / "aq_sol.sqlite"


def get_engine(db_file: Path = DB_FILE) -> Engine:
    return create_engine(f"sqlite:///{db_file}")


def create_aq_sol_table(table_name: str = "aq_sol") -> int:
    with get_engine().connect() as conn:
        drop = text(f"DROP TABLE  IF EXISTS  {table_name}")
        conn.execute(drop)

        df = get_solubility_df()
        df["Ocurrences"] = df.Ocurrences.astype(np.int32)

        df.to_sql(table_name, conn, index=False)

        meta = MetaData()
        meta.reflect(bind=conn)
        table = Table(table_name, meta, autoload_with=conn)
        with sessionmaker(bind=conn)() as sess:
            query = select(func.count()).select_from(table)
            num_rows = sess.execute(query).scalar()
            assert isinstance(num_rows, int)
            return num_rows
