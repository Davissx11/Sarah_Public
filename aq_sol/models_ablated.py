#! /usr/bin/env YDATA_SUPPRESS_BANNER=1 python


import pandas as pd

from aq_sol.eda import get_solubility_df
from aq_sol.models import (
    add_confounds,
    create_gbr_model,
    create_rf_model,
    create_svm_model,
    create_xgb_model,
    shuffle,
    text_cols,
)


def create_ablated_models() -> None:
    df = shuffle(get_solubility_df())
    df = df.drop(labels=text_cols, axis="columns")
    df = df.dropna()  # no missing values in this dataset, so this drops nothing
    df = add_confounds(df, 0)
    assert len(df) == 9_982, len(df)

    x = df.drop("solubility", axis="columns")
    y = pd.DataFrame(df["solubility"])

    create_svm_model(x, y)
    create_gbr_model(x, y)
    create_rf_model(x, y)

    create_xgb_model(x, y)


if __name__ == "__main__":
    create_ablated_models()
