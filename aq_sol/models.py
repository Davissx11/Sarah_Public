#! /usr/bin/env YDATA_SUPPRESS_BANNER=1 python

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import xgboost as xgb
from numpy.typing import NDArray
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from xgboost.sklearn import XGBRegressor

from aq_sol.eda import TMP, get_solubility_df


def shuffle(df: pd.DataFrame) -> pd.DataFrame:
    return df.sample(frac=1, random_state=42)


SEED = 42

FltArr = NDArray[np.float64]


def _arr(a: pd.DataFrame | list[None]) -> FltArr:
    assert isinstance(a, pd.DataFrame)
    return np.array(a, dtype=np.float64)


def _train_test_split(
    x: pd.DataFrame,
    y: pd.DataFrame,
    test_holdout_fraction: float = 0.2,
    *,
    random_seed: int = SEED,
) -> tuple[FltArr, FltArr, FltArr, FltArr]:
    x_train, x_test, y_train, y_test = map(
        _arr,
        train_test_split(x, y, test_size=test_holdout_fraction, random_state=random_seed),
    )
    return x_train, x_test, y_train.ravel(), y_test.ravel()


def _z_scale(x: pd.DataFrame) -> pd.DataFrame:
    scaler = StandardScaler()
    for col in x.columns:
        x[col] = scaler.fit_transform(np.array(x[col]).reshape(-1, 1))
    return x


def create_models() -> None:
    text_cols = ["ID", "Name", "InChI", "InChIKey", "SMILES", "Group"]
    df = shuffle(get_solubility_df())
    df = df.drop(labels=text_cols, axis="columns")
    df = df.dropna()  # no missing values in this dataset, so this drops nothing
    rng = np.random.default_rng(seed=42)
    for i in range(20):
        df[f"confound{i + 1 :02}"] = rng.random(size=len(df))
    assert len(df) == 9_982, len(df)

    x = df.drop("Solubility", axis="columns")
    y = pd.DataFrame(df["Solubility"])

    create_svm_model(x, y)
    create_gbr_model(x, y)
    create_rf_model(x, y)

    xgb_model = create_xgb_model(x, y)
    show_importance(xgb_model, x.columns)
    plot_tree(xgb_model, _create_feature_map(x))


def _create_feature_map(x: pd.DataFrame) -> Path:
    fmap = Path(TMP) / "xgboost_feature_map.txt"
    with fmap.open("w") as fout:
        for i, name in enumerate(x.columns):
            fout.write(f"{i:3}  {name:<20} q\n")
    return fmap


def create_svm_model(x: pd.DataFrame, y: pd.DataFrame, *, want_charts: bool = False) -> None:
    x_train, x_test, y_train, y_test = _train_test_split(x, y)

    scaler = StandardScaler()
    x_train = np.array(scaler.fit_transform(x_train))
    x_test = np.array(scaler.transform(x_test))

    svm_model = SVR(kernel="rbf", C=1.0, gamma="scale")

    svm_model.fit(x_train, y_train)

    _evaluate_error("SVM", svm_model, x_test, y_test)

    if want_charts:
        plot(y_test, svm_model.predict(x_test))


def create_gbr_model(x: pd.DataFrame, y: pd.DataFrame, *, want_charts: bool = False) -> None:
    x_train, x_test, y_train, y_test = _train_test_split(x, y)

    gbr_model = GradientBoostingRegressor(random_state=SEED)

    gbr_model.fit(x_train, y_train)

    _evaluate_error("GBR", gbr_model, x_test, y_test)

    if want_charts:
        plot(y_test, gbr_model.predict(x_test))


def create_rf_model(x: pd.DataFrame, y: pd.DataFrame, *, want_charts: bool = False) -> None:
    x_train, x_test, y_train, y_test = _train_test_split(x, y)

    rf_model = RandomForestRegressor(n_estimators=100, random_state=SEED)
    rf_model.fit(x_train, y_train)

    _evaluate_error("RF ", rf_model, x_test, y_test)

    if want_charts:
        plot(y_test, rf_model.predict(x_test))


def create_xgb_model(
    x: pd.DataFrame,
    y: pd.DataFrame,
    *,
    want_charts: bool = False,
) -> XGBRegressor:
    x_train, x_test, y_train, y_test = _train_test_split(x, y)
    y_test = np.array(y_test)

    xgb_model = XGBRegressor(objective="reg:squarederror", n_estimators=100, random_state=SEED)
    xgb_model.fit(x_train, y_train)
    _evaluate_error("XGB", xgb_model, x_test, y_test)

    if want_charts:
        plot(y_test, xgb_model.predict(x_test))

    return xgb_model


def show_importance(model: XGBRegressor, feature_names: pd.Index) -> None:
    imp_series = pd.Series(
        data=model.feature_importances_,
        index=feature_names,
    )
    imp_df = imp_series.to_frame(name="Importance")
    imp_df = imp_df.sort_values(by="Importance", ascending=False)
    with pd.option_context("display.float_format", "{:.3f}".format):
        print("\nTop Feature Importances:")
        print(imp_df.head(4))


def _evaluate_error(
    label: str,
    model: GradientBoostingRegressor | MLPRegressor | RandomForestRegressor | SVR | XGBRegressor,
    x_test: FltArr,
    y_test: FltArr,
) -> None:
    y_pred = model.predict(x_test)
    print()
    print(label, "RMSE:", round(mean_squared_error(y_test, y_pred), 4))
    print(label, "MAE: ", round(mean_absolute_error(y_test, y_pred), 4))


def _set_high_res_font_params() -> None:
    mpl.rcParams.update(
        {
            "font.size": 12,
            "axes.titlesize": 14,
            "axes.labelsize": 12,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "legend.fontsize": 12,
            "xtick.major.size": 5,
            "ytick.major.size": 5,
        },
    )


def plot_tree(
    model: XGBRegressor,
    feature_map: Path,
    out_file: Path = TMP / "tree.pdf",
    dpi: int = 1800,
) -> None:
    _set_high_res_font_params()
    xgb.plot_tree(model, tree_idx=0, rankdir="LR", fmap=feature_map)
    plt.savefig(out_file, dpi=dpi, bbox_inches="tight")


def plot(y_test: FltArr, y_pred: FltArr) -> None:

    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=y_test, y=y_pred, label="Predictions vs. Actual")
    plt.xlabel("Actual Solubility")
    plt.ylabel("Predicted Solubility")
    plt.title("XGBoost Solubility Prediction")
    plt.legend()
    plt.show()

    plt.figure(figsize=(10, 6))
    sns.histplot(y_test - y_pred, bins=20, kde=True)
    plt.xlabel("Residuals")
    plt.ylabel("Frequency")
    plt.title("Residual Plot")
    plt.show()


if __name__ == "__main__":
    create_models()
