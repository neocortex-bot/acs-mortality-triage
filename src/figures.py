"""Publication figures for the ACS mortality triage analysis."""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve

from .config import ANALYSIS_RESULTS_PATH, FIGURES_DIR, PALETTE


def _load_results() -> dict:
    with ANALYSIS_RESULTS_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save(fig: plt.Figure, name: str) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / name, dpi=300, bbox_inches="tight")
    plt.close(fig)


def fig_roc(results: dict) -> None:
    pred = results["oof_predictions"]
    y = np.array(pred["y_true"])
    p = np.array(pred["model_probability"])
    g = np.array(pred["grace_2_0"])
    fpr_m, tpr_m, _ = roc_curve(y, p)
    fpr_g, tpr_g, _ = roc_curve(y, g)
    comp = results["grace_comparison"]
    fig, ax = plt.subplots(figsize=(6.5, 5.2))
    ax.plot(fpr_m, tpr_m, color=PALETTE["blue"], lw=2.5, label=f"Model AUC {comp['model_auc']:.3f}")
    ax.plot(fpr_g, tpr_g, color=PALETTE["orange"], lw=2.5, label=f"GRACE 2.0 AUC {comp['grace_auc']:.3f}")
    ax.plot([0, 1], [0, 1], color="#999999", lw=1, ls=":")
    ax.set_xlabel("False positive rate", fontsize=12)
    ax.set_ylabel("True positive rate", fontsize=12)
    ax.set_title("Discrimination in pooled out-of-fold predictions", fontsize=13)
    ax.text(0.52, 0.20, f"AUC difference {comp['delta_auc']:.3f}\nDeLong p = {comp['p_value']:.3f}", fontsize=10)
    ax.legend(loc="lower right", frameon=False, fontsize=10)
    _save(fig, "fig1_roc.png")


def fig_calibration(results: dict) -> None:
    pred = results["oof_predictions"]
    y = np.array(pred["y_true"])
    p = np.array(pred["model_probability"])
    df = pd.DataFrame({"y": y, "p": p}).sort_values("p", kind="mergesort")
    bins = [df.iloc[idx] for idx in np.array_split(np.arange(len(df)), 10)]
    mean_p = [b["p"].mean() for b in bins]
    obs = [b["y"].mean() for b in bins]
    cal = results["main"]["calibration"]
    fig, ax = plt.subplots(figsize=(6.2, 5.2))
    ax.plot([0, 1], [0, 1], color="#999999", lw=1, ls=":")
    ax.plot(mean_p, obs, marker="o", color=PALETTE["green"], lw=2.5)
    ax.set_xlim(0, max(0.65, max(mean_p) * 1.1))
    ax.set_ylim(0, max(0.75, max(obs) * 1.1))
    ax.set_xlabel("Mean predicted risk", fontsize=12)
    ax.set_ylabel("Observed mortality", fontsize=12)
    ax.set_title("Calibration across equal-frequency bins", fontsize=13)
    ax.text(
        0.03,
        0.62,
        f"Slope {cal['slope']:.3f}\nCITL {cal['citl']:.3f}\nO:E {cal['oe_ratio']:.3f}\nECE {cal['ece']:.3f}",
        fontsize=10,
        bbox={"facecolor": "white", "edgecolor": "#dddddd"},
    )
    _save(fig, "fig2_calibration.png")


def fig_tiers(results: dict) -> None:
    tiers = results["main"]["tiers"]
    labels = ["HIGH", "INTERMEDIATE", "LOW", "NOT_FLAGGED"]
    keys = ["high", "intermediate", "low", "not_flagged"]
    n = [tiers[k]["n"] for k in keys]
    deaths = [tiers[k]["deaths"] for k in keys]
    ppv = [tiers[k]["ppv"] for k in keys]
    colors = [PALETTE["red"], PALETTE["orange"], PALETTE["yellow"], PALETTE["dark"]]
    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    bars = ax.bar(labels, n, color=colors)
    ax.set_ylabel("Patients", fontsize=12)
    ax.set_title("Tier allocation at fixed screening threshold 0.08", fontsize=13)
    for bar, ni, di, pi in zip(bars, n, deaths, ppv):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 18,
            f"n={ni}\ndeaths={di}\nPPV={pi*100:.1f}%",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    ax.set_ylim(0, max(n) * 1.22)
    _save(fig, "fig3_tiers.png")


def fig_flow(results: dict) -> None:
    cohort = results["cohort"]
    stage1 = results["main"]["stage1"]
    tiers = results["main"]["tiers"]
    flagged_n = stage1["tp"] + stage1["fp"]
    fig, ax = plt.subplots(figsize=(8, 5.2))
    ax.axis("off")
    boxes = [
        (0.50, 0.86, f"ACS cohort\nn={cohort['n']:,}\n{cohort['deaths']} deaths"),
        (0.30, 0.62, f"Flagged for review\nn={flagged_n}\n{stage1['tp']} deaths"),
        (0.72, 0.62, f"Standard care\nn={tiers['not_flagged']['n']:,}\n{tiers['not_flagged']['deaths']} deaths"),
        (0.16, 0.30, f"HIGH RISK\nconsider ICU\nn={tiers['high']['n']}, PPV {tiers['high']['ppv']*100:.1f}%"),
        (0.42, 0.30, f"INTERMEDIATE\nconsider HCU\nn={tiers['intermediate']['n']}, PPV {tiers['intermediate']['ppv']*100:.1f}%"),
        (0.68, 0.30, f"LOW RISK\nconsider ward\nn={tiers['low']['n']}, PPV {tiers['low']['ppv']*100:.1f}%"),
    ]
    for x, y, text in boxes:
        ax.text(x, y, text, ha="center", va="center", fontsize=11, bbox={"boxstyle": "round,pad=0.35", "fc": "white", "ec": PALETTE["dark"], "lw": 1.4})
    arrows = [((0.45, 0.80), (0.32, 0.68)), ((0.55, 0.80), (0.70, 0.68)), ((0.26, 0.55), (0.16, 0.38)), ((0.30, 0.55), (0.42, 0.38)), ((0.34, 0.55), (0.68, 0.38))]
    for start, end in arrows:
        ax.annotate("", xy=end, xytext=start, arrowprops={"arrowstyle": "->", "lw": 1.5, "color": PALETTE["dark"]})
    ax.text(0.5, 0.08, "Advisory referral-center monitoring support. Treating clinicians retain all decisions.", ha="center", fontsize=10)
    _save(fig, "fig4_flow.png")


def fig_threshold_tradeoff(results: dict) -> None:
    rows = results["threshold_tradeoff"]
    x = [r["false_positives"] for r in rows]
    y = [r["system"]["sensitivity"] * 100 for r in rows]
    labels = [str(r["threshold"]) for r in rows]
    fig, ax = plt.subplots(figsize=(6.5, 5.0))
    ax.plot(x, y, marker="o", color=PALETTE["blue"], lw=2.5)
    for xi, yi, lab in zip(x, y, labels):
        ax.text(xi + 5, yi, f"t={lab}", fontsize=9)
    ax.set_xlabel("False positives among escalated patients", fontsize=12)
    ax.set_ylabel("System sensitivity (%)", fontsize=12)
    ax.set_title("Threshold trade-off with fixed tier split", fontsize=13)
    _save(fig, "fig5_threshold_tradeoff.png")


def fig_dca(results: dict) -> None:
    pred = results["oof_predictions"]
    y = np.array(pred["y_true"])
    p = np.array(pred["model_probability"])
    thresholds = np.linspace(0.01, 0.40, 80)
    prevalence = y.mean()
    model_nb = []
    all_nb = []
    none_nb = np.zeros_like(thresholds)
    for t in thresholds:
        pred_pos = p >= t
        tp = np.sum(pred_pos & (y == 1))
        fp = np.sum(pred_pos & (y == 0))
        n = len(y)
        model_nb.append(tp / n - fp / n * (t / (1 - t)))
        all_nb.append(prevalence - (1 - prevalence) * (t / (1 - t)))
    fig, ax = plt.subplots(figsize=(6.5, 5.0))
    ax.plot(thresholds, model_nb, color=PALETTE["blue"], lw=2.5, label="Model")
    ax.plot(thresholds, all_nb, color=PALETTE["orange"], lw=2, label="Treat all")
    ax.plot(thresholds, none_nb, color=PALETTE["dark"], lw=2, ls=":", label="Treat none")
    ax.set_xlabel("Risk threshold", fontsize=12)
    ax.set_ylabel("Net benefit", fontsize=12)
    ax.set_title("Decision curve analysis", fontsize=13)
    ax.legend(frameon=False)
    _save(fig, "fig6_dca.png")


def generate_figures() -> None:
    results = _load_results()
    fig_roc(results)
    fig_calibration(results)
    fig_tiers(results)
    fig_flow(results)
    fig_threshold_tradeoff(results)
    fig_dca(results)


if __name__ == "__main__":
    generate_figures()
