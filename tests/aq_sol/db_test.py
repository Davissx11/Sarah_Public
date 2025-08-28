import unittest

from sqlalchemy import MetaData, Table, func, select
from sqlalchemy.orm import sessionmaker

from aq_sol.db import create_aq_sol_table, get_engine


class DbTest(unittest.TestCase):

    def test_count(self) -> None:
        table_name = create_aq_sol_table()

        with sessionmaker(bind=get_engine())() as sess:
            meta = MetaData()
            meta.reflect(bind=sess.get_bind())
            table = Table(table_name, meta, autoload_with=sess.get_bind())

            query = select(func.count()).select_from(table)
            num_rows = sess.execute(query).scalar()
            assert isinstance(num_rows, int)
            self.assertEqual(9_982, num_rows)
