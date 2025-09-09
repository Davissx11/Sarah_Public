#! /usr/bin/env YDATA_SUPPRESS_BANNER=1 python

import re
from collections.abc import Generator
from pathlib import Path
from subprocess import check_call

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

from aq_sol.eda import TMP


def main(log: Path = TMP / "ablated.txt") -> None:
    assert Path("aq_sol").exists()  # Please cd to repo top before running this script.
    if not log.exists():
        cmd = f"aq_sol/ablated_models.py  > {log}"
        check_call(cmd, shell=True)
    df = pd.DataFrame(parse_ablation_log(log))
    num_models = 4
    plot(pd.DataFrame(df[:-num_models]))  # Omit the final trial.


def parse_ablation_log(log: Path) -> Generator[dict[str, float | str]]:
    trial_re = re.compile(r"^trial +(\d+)")
    mae_re = re.compile(r"^(\w+) +MAE: +(.*)")  # We ignore MSE.
    with log.open() as fin:
        trial = 0
        name = ""
        mae = 0.0
        for line in fin:
            if m := trial_re.search(line):
                trial = int(m[1])
            if m := mae_re.search(line):
                name = m[1]
                mae = float(m[2])
                yield {
                    "trial": trial,
                    "name": name,
                    "mae": mae,
                }


def plot(df: pd.DataFrame) -> None:
    sns.pointplot(data=df, x="trial", y="mae", hue="name")
    plt.savefig(TMP / "ablated.pdf")
    plt.show()


if __name__ == "__main__":
    main()
