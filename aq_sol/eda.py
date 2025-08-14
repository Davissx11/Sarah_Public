#! /usr/bin/env YDATA_SUPPRESS_BANNER=1 python

# from:
# https://www.kaggle.com/code/kerneler/starter-aqsoldb-a-curated-aqueous-6146b12d-1
# cf https://www.nature.com/articles/s41597-019-0151-1

from pathlib import Path

import kagglehub
import pandas as pd
from ydata_profiling import ProfileReport

TMP = Path("/tmp")


def get_solubility_df() -> pd.DataFrame:
    dataset = "sorkun/aqsoldb-a-curated-aqueous-solubility-dataset"
    folder = Path(kagglehub.dataset_download(dataset))
    csv = folder / "curated-solubility-dataset.csv"
    return pd.read_csv(csv)


def create_profile() -> None:
    profile = ProfileReport(get_solubility_df(), title="Solubility Profiling Report")
    html = TMP / "solubility.html"
    if not html.exists():
        profile.to_file(html)


if __name__ == "__main__":
    create_profile()
