import unittest
from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import MetaData, Table, func, select
from sqlalchemy.orm import Session, sessionmaker

from aq_sol.db import create_aq_sol_table, get_engine


@contextmanager
def get_session_meta() -> Generator[tuple[Session, MetaData], None, None]:
    engine = get_engine()
    session = sessionmaker(bind=engine)()
    meta = MetaData()
    meta.reflect(bind=engine)
    try:
        yield session, meta
    finally:
        session.close()


class DbTest(unittest.TestCase):

    def test_count(self) -> None:
        table_name = create_aq_sol_table()

        with get_session_meta() as (sess, meta):
            table = Table(table_name, meta, autoload_with=sess.get_bind())

            query = select(func.count()).select_from(table)
            num_rows = sess.execute(query).scalar()
            self.assertEqual(9_982, num_rows)
