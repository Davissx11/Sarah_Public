#! /usr/bin/env YDATA_SUPPRESS_BANNER=1 python

# from:
# https://www.kaggle.com/code/kerneler/starter-aqsoldb-a-curated-aqueous-6146b12d-1
# cf https://www.nature.com/articles/s41597-019-0151-1

import re
from pathlib import Path

import kagglehub
import pandas as pd
from ydata_profiling import ProfileReport

TMP = Path("/tmp")
DESKTOP = Path("~/Desktop").expanduser()


def to_snake_case(s: str) -> str:
    """FooBar --> foo_bar."""
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", s)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def get_solubility_df() -> pd.DataFrame:
    dataset = "sorkun/aqsoldb-a-curated-aqueous-solubility-dataset"
    folder = Path(kagglehub.dataset_download(dataset))
    csv = folder / "curated-solubility-dataset.csv"
    df = pd.read_csv(csv)

    # Downcase the column names; verify they are sane.
    for col in df.columns:
        assert " " not in col
        assert col.isalpha()
        df = df.rename({col: to_snake_case(col)}, axis="columns")

    df["name"] = df.name.str.strip()
    return df


def create_profile() -> None:
    profile = ProfileReport(get_solubility_df(), title="Solubility Profiling Report")
    html = TMP / "solubility.html"
    if not html.exists():
        profile.to_file(html)
        print(f"You may now view {html} in a browser.")


if __name__ == "__main__":
    create_profile()
