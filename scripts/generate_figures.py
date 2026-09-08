"""Regenerate public Figure 2 and Figure 4 from frozen aggregate outputs only."""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reproduced_figures"
BLUE, ORANGE, GRAY = "#0072B2", "#D55E00", "#6E6E6E"


def save(fig, name: str) -> None:
    OUT.mkdir(exist_ok=True)
    for suffix, kwargs in [("svg", {}), ("pdf", {}), ("png", {"dpi": 600})]:
        fig.savefig(OUT / f"{name}.{suffix}", bbox_inches="tight", facecolor="white", **kwargs)
    plt.close(fig)


def figure_2(macro: pd.DataFrame) -> None:
    order = ["RANDOM", "GROUP_STUDY", "LOSO"]
    values = macro.set_index("regime").loc[order]
    x = np.arange(3)
    fig, axes = plt.subplots(1, 2, figsize=(7.15, 3.45), gridspec_kw={"wspace": .35})
    for name, colour in [("PREVALENCE", GRAY), ("LR", BLUE), ("RF", ORANGE)]:
        axes[0].plot(x, values[name], color=colour, marker="o", label=name.title())
    axes[0].set_xticks(x, ["Random", "Study-grouped", "LOSO"])
    axes[0].set_ylabel("Macro Brier loss")
    axes[0].legend(frameon=False)
    for name, colour in [("LR", BLUE), ("RF", ORANGE)]:
        axes[1].plot(x, values["BSS_" + name], color=colour, marker="o", label=name)
    axes[1].axhline(0, color="#303030", lw=.8)
    axes[1].set_xticks(x, ["Random", "Study-grouped", "LOSO"])
    axes[1].set_ylabel("Macro BSS versus training prevalence")
    axes[1].legend(frameon=False)
    save(fig, "Figure_2_reproduced")


def figure_4(gaps: pd.DataFrame) -> None:
    labels = ["APOE", "APOB", "C3", "CLUS", "Macro"]
    targets = ["APOE", "APOB", "CO3", "CLUS", "OVERALL_MACRO"]
    fig, axes = plt.subplots(1, 2, figsize=(7.15, 3.5), sharey=True, gridspec_kw={"wspace": .16})
    for ax, regime, title in zip(axes, ["GROUP_STUDY", "LOSO"], ["STUDY-GROUPED - RANDOM", "LOSO - RANDOM"]):
        for model, colour, offset in [("LR", BLUE, .14), ("RF", ORANGE, -.14)]:
            subset = gaps[(gaps.regime == regime) & (gaps.model == model)].set_index("target").loc[targets]
            y = np.arange(len(targets)) + offset
            ax.errorbar(subset.gap, y, xerr=[subset.gap - subset.ci_low, subset.ci_high - subset.gap], fmt="o", color=colour, capsize=2, label=model)
        ax.axvline(0, color="#303030", lw=.8)
        ax.set_title(title)
        ax.set_xlabel("Difference in Brier loss")
    axes[0].set_yticks(np.arange(len(labels)), labels)
    axes[0].legend(frameon=False)
    save(fig, "Figure_4_reproduced")


def main() -> None:
    macro = pd.read_csv(ROOT / "aggregate_results" / "bss_overall_macro.csv")
    gaps = pd.read_csv(ROOT / "aggregate_results" / "gap_uncertainty.csv")
    figure_2(macro)
    figure_4(gaps)
    print("Regenerated Figure 2 and Figure 4 from frozen aggregate outputs.")


if __name__ == "__main__":
    main()
