"""Metrics for model performance, calibration, and AUC comparison."""

from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats
from scipy.special import logit
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, roc_auc_score


def binary_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, Any]:
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    ppv = tp / (tp + fp) if tp + fp else math.nan
    npv = tn / (tn + fn) if tn + fn else math.nan
    return {
        "tp": int(tp),
        "fp": int(fp),
        "fn": int(fn),
        "tn": int(tn),
        "sensitivity": float(tp / (tp + fn)),
        "specificity": float(tn / (tn + fp)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "ppv": float(ppv),
        "npv": float(npv),
    }


def ece(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> float:
    """Expected calibration error with equal-frequency bins."""
    df = pd.DataFrame({"y": y_true, "p": y_prob}).sort_values("p", kind="mergesort")
    bins = [df.iloc[idx] for idx in np.array_split(np.arange(len(df)), n_bins)]
    total = len(df)
    err = 0.0
    for b in bins:
        if len(b) == 0:
            continue
        err += (len(b) / total) * abs(float(b["y"].mean()) - float(b["p"].mean()))
    return float(err)


def calibration_metrics(y_true: np.ndarray, y_prob: np.ndarray) -> dict[str, float]:
    eps = 1e-6
    p = np.clip(y_prob, eps, 1 - eps)
    lp = logit(p).reshape(-1, 1)
    model = LogisticRegression(C=np.inf, solver="lbfgs", max_iter=1000)
    model.fit(lp, y_true)
    observed = float(np.sum(y_true))
    expected = float(np.sum(y_prob))
    return {
        "slope": float(model.coef_[0, 0]),
        "citl": float(logit(np.mean(y_true)) - logit(np.mean(y_prob))),
        "oe_ratio": float(observed / expected),
        "ece": ece(y_true, y_prob, n_bins=10),
    }


def _compute_midrank(x: np.ndarray) -> np.ndarray:
    order = np.argsort(x)
    sorted_x = x[order]
    n = len(x)
    ranks = np.zeros(n, dtype=float)
    i = 0
    while i < n:
        j = i
        while j < n and sorted_x[j] == sorted_x[i]:
            j += 1
        ranks[order[i:j]] = 0.5 * (i + j - 1) + 1
        i = j
    return ranks


def _fast_delong(predictions_sorted: np.ndarray, label_1_count: int) -> tuple[np.ndarray, np.ndarray]:
    m = label_1_count
    n = predictions_sorted.shape[1] - m
    positive_examples = predictions_sorted[:, :m]
    negative_examples = predictions_sorted[:, m:]
    k = predictions_sorted.shape[0]
    tx = np.empty((k, m))
    ty = np.empty((k, n))
    tz = np.empty((k, m + n))
    for r in range(k):
        tx[r, :] = _compute_midrank(positive_examples[r, :])
        ty[r, :] = _compute_midrank(negative_examples[r, :])
        tz[r, :] = _compute_midrank(predictions_sorted[r, :])
    aucs = tz[:, :m].sum(axis=1) / m / n - (m + 1.0) / 2.0 / n
    v01 = (tz[:, :m] - tx) / n
    v10 = 1.0 - (tz[:, m:] - ty) / m
    sx = np.cov(v01)
    sy = np.cov(v10)
    delongcov = sx / m + sy / n
    return aucs, np.atleast_2d(delongcov)


def delong_roc_test(y_true: np.ndarray, prob_a: np.ndarray, prob_b: np.ndarray) -> dict[str, float]:
    y_true = np.asarray(y_true)
    order = np.argsort(-y_true)
    preds = np.vstack((prob_a, prob_b))[:, order]
    label_1_count = int(np.sum(y_true))
    aucs, cov = _fast_delong(preds, label_1_count)
    diff = float(aucs[0] - aucs[1])
    var = float(cov[0, 0] + cov[1, 1] - 2 * cov[0, 1])
    se = math.sqrt(max(var, 0.0))
    z = diff / se if se else math.inf
    p = 2 * stats.norm.sf(abs(z))
    ci_low = diff - 1.96 * se
    ci_high = diff + 1.96 * se
    return {
        "model_auc": float(roc_auc_score(y_true, prob_a)),
        "grace_auc": float(roc_auc_score(y_true, prob_b)),
        "delta_auc": diff,
        "se": float(se),
        "z": float(z),
        "p_value": float(p),
        "ci_low": float(ci_low),
        "ci_high": float(ci_high),
    }
