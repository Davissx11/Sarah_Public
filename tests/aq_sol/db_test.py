import unittest

from aq_sol.db import create_aq_sol_table


class DbTest(unittest.TestCase):
    def test_count(self) -> None:
        create_aq_sol_table()
