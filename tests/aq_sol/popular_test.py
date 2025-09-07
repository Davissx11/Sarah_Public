import re
import unittest

import pandas as pd

from aq_sol.eda import DESKTOP, get_solubility_df
from aq_sol.popular import PopCache, popularity

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
        title, pv = popularity("Potassium_chloride")
        self.assertEqual("Potassium_chloride", title)
        self.assertGreater(pv, 19_000)  # 19_710

    def test_add_names(self, max_width: int = 40) -> None:
        pc = PopCache()
        # pc.DB_FILE.unlink()
        pc = PopCache()

        df = get_solubility_df().sort_values(by="name")
        df["name"] = df.name.apply(lambda x: str(x)[:max_width])
        df = df[["name", "mol_wt", "mol_log_p", "balaban_j", "solubility"]]
        df.to_csv(DESKTOP / "sol.csv", index=False)

        # For now, focus on just the rows whose .name starts with capital "A".
        assert isinstance(df.name, pd.Series)
        df_a = pd.DataFrame(df[df.name.str.match(r"^[A-M]")])
        names = sorted(map(str, df_a.name))
        self.assertEqual(228, len(names))

        pc.add_names(names[2:])
