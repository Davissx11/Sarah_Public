import re
import unittest

from aq_sol.eda import get_solubility_df
from aq_sol.popular import popular

_comma_first_phrase = re.compile(r"(.+) *,")
_sem_last_phrase = re.compile(r".*; *(.+)")


def _minimal_punctuation(name: str) -> bool:
    name = name.strip()
    for fn in [_comma_first_phrase, _sem_last_phrase]:
        m = fn.search(name)
        if m:
            name = m.group(1)

    return "-" not in name and "(" not in name


def _get_names() -> list[str]:
    names = set(filter(_minimal_punctuation, get_solubility_df().Name))
    return sorted(map(str.capitalize, names))


class PopularTest(unittest.TestCase):

    def test_popular(self) -> None:
        self.assertEqual(19_714, popular("Potassium_chloride"))
