"""End-to-end analysis for the single-stage ACS mortality triage model."""

from __future__ import annotations

import json
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import brier_score_loss, roc_auc_score, roc_curve
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline

from .config import (
    ANALYSIS_RESULTS_PATH,
    CANONICAL,
    CORE12,
    INNER_SPLITS,
    OUTER_SPLITS,
    RANDOM_STATE,
    RF_PARAMS,
    SCREENING_THRESHOLD,
    YOUDEN_REFERENCE_THRESHOLD,
)
from .data import load_data
from .metrics import binary_metrics, calibration_metrics, delong_roc_test


def _json_default(obj: Any) -> Any:
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj)!r} is not JSON serializable")


def make_model() -> Pipeline:
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("model", RandomForestClassifier(**RF_PARAMS)),
        ]
    )


def nested_oof_predictions(data: pd.DataFrame, features: list[str]) -> dict[str, Any]:
    X = data[features]
    y = data["inhospital_death"].astype(int).to_numpy()
    outer = StratifiedKFold(n_splits=OUTER_SPLITS, shuffle=True, random_state=RANDOM_STATE)
    inner = StratifiedKFold(n_splits=INNER_SPLITS, shuffle=True, random_state=RANDOM_STATE)
    oof = np.zeros(len(data), dtype=float)
    importances = []
    inner_youden = []

    for train_idx, test_idx in outer.split(X, y):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train = y[train_idx]
        inner_oof = np.zeros(len(train_idx), dtype=float)
        for inner_train_idx, inner_valid_idx in inner.split(X_train, y_train):
            model = make_model()
            model.fit(X_train.iloc[inner_train_idx], y_train[inner_train_idx])
            inner_oof[inner_valid_idx] = model.predict_proba(X_train.iloc[inner_valid_idx])[:, 1]
        fpr, tpr, thresholds = roc_curve(y_train, inner_oof)
        j = tpr - fpr
        inner_youden.append(float(thresholds[np.argmax(j)]))

        model = make_model()
        model.fit(X_train, y_train)
        oof[test_idx] = model.predict_proba(X_test)[:, 1]
        importances.append(model.named_steps["model"].feature_importances_)

    return {
        "probabilities": oof,
        "inner_youden_thresholds": inner_youden,
        "feature_importance": dict(zip(features, np.mean(importances, axis=0))),
    }


def assign_tiers(prob: np.ndarray, flagged: np.ndarray) -> np.ndarray:
    tiers = np.array(["NOT_FLAGGED"] * len(prob), dtype=object)
    flagged_idx = np.where(flagged)[0]
    order = flagged_idx[np.argsort(-prob[flagged_idx], kind="mergesort")]
    n = len(order)
    high_end = int(np.floor(n * 0.25))
    intermediate_end = high_end + int(np.floor(n * 0.50))
    tiers[order[:high_end]] = "HIGH"
    tiers[order[high_end:intermediate_end]] = "INTERMEDIATE"
    tiers[order[intermediate_end:]] = "LOW"
    return tiers


def tier_summary(y: np.ndarray, tiers: np.ndarray) -> dict[str, dict[str, Any]]:
    out = {}
    for label in ["HIGH", "INTERMEDIATE", "LOW", "NOT_FLAGGED"]:
        mask = tiers == label
        deaths = int(y[mask].sum())
        n = int(mask.sum())
        out[label.lower()] = {
            "n": n,
            "deaths": deaths,
            "survivors": int(n - deaths),
            "ppv": float(deaths / n) if n else None,
        }
    return out


def system_at_threshold(y: np.ndarray, prob: np.ndarray, threshold: float) -> dict[str, Any]:
    flagged = prob >= threshold
    tiers = assign_tiers(prob, flagged)
    escalated = np.isin(tiers, ["HIGH", "INTERMEDIATE"])
    metrics = binary_metrics(y, escalated.astype(int))
    stage1 = binary_metrics(y, flagged.astype(int))
    return {
        "threshold": float(threshold),
        "flagged_n": int(flagged.sum()),
        "flagged_deaths": int(y[flagged].sum()),
        "escalated_n": int(escalated.sum()),
        "missed_deaths": int(metrics["fn"]),
        "false_positives": int(metrics["fp"]),
        "system": metrics,
        "stage1": stage1,
        "tiers": tier_summary(y, tiers),
    }


def missingness(data: pd.DataFrame) -> dict[str, Any]:
    rows = []
    for col in CORE12:
        missing = int(data[col].isna().sum())
        rows.append({"variable": col, "missing_n": missing, "missing_pct": float(missing / len(data))})
    complete_case = int(data[CORE12].notna().all(axis=1).sum())
    any_missing = int(data[CORE12].isna().any(axis=1).sum())
    return {
        "per_variable": rows,
        "complete_case_n": complete_case,
        "complete_case_pct": float(complete_case / len(data)),
        "any_missing_n": any_missing,
        "any_missing_pct": float(any_missing / len(data)),
    }


def shock_crosstabs(data: pd.DataFrame) -> dict[str, Any]:
    y = data["inhospital_death"].astype(int)
    killip_iv = data["killip"] == 4
    cs = data["cardiogenic_shock"] == 1
    soa = data["shock_on_arrival"] == 1
    cs_without_soa = cs & ~soa
    soa_without_cs = soa & ~cs
    return {
        "killip_iv_n": int(killip_iv.sum()),
        "cardiogenic_shock_n": int(cs.sum()),
        "shock_on_arrival_n": int(soa.sum()),
        "soa_without_cs_n": int(soa_without_cs.sum()),
        "cs_without_killip_iv_n": int((cs & ~killip_iv).sum()),
        "death_rate_killip_iv": float(y[killip_iv].mean()),
        "death_rate_shock_on_arrival": float(y[soa].mean()),
        "death_rate_cardiogenic_shock": float(y[cs].mean()),
        "death_rate_cs_without_soa": float(y[cs_without_soa].mean()),
        "death_rate_cs_without_killip_iv": float(y[cs & ~killip_iv].mean()),
    }


def guardrail_checks(results: dict[str, Any]) -> list[str]:
    checks = []
    stage1 = results["main"]["stage1"]
    tiers = results["main"]["tiers"]
    system = results["main"]["system"]
    expected = {
        "stage1_flagged": stage1["tp"] + stage1["fp"],
        "stage1_deaths": stage1["tp"],
        "stage1_survivors": stage1["fp"],
        "tier_high_n": tiers["high"]["n"],
        "tier_high_deaths": tiers["high"]["deaths"],
        "tier_intermediate_n": tiers["intermediate"]["n"],
        "tier_intermediate_deaths": tiers["intermediate"]["deaths"],
        "tier_low_n": tiers["low"]["n"],
        "tier_low_deaths": tiers["low"]["deaths"],
        "system_tp": system["tp"],
        "system_fp": system["fp"],
        "system_fn": system["fn"],
        "system_tn": system["tn"],
    }
    for key, actual in expected.items():
        if int(actual) != int(CANONICAL[key]):
            raise AssertionError(f"{key}: expected {CANONICAL[key]}, got {actual}")
        checks.append(f"PASS {key} = {actual}")
    return checks


def run_analysis(write_json: bool = True) -> dict[str, Any]:
    data = load_data()
    y = data["inhospital_death"].astype(int).to_numpy()

    main_pred = nested_oof_predictions(data, CORE12)
    prob = main_pred["probabilities"]
    main = system_at_threshold(y, prob, SCREENING_THRESHOLD)
    main["auc"] = float(roc_auc_score(y, prob))
    main["brier"] = float(brier_score_loss(y, prob))
    main["calibration"] = calibration_metrics(y, prob)
    main["feature_importance"] = main_pred["feature_importance"]
    main["inner_youden_thresholds"] = main_pred["inner_youden_thresholds"]
    main["youden_reference_threshold"] = YOUDEN_REFERENCE_THRESHOLD
    main["epv"] = float(main["stage1"]["tp"] / len(CORE12))

    grace_prob = data["grace_2_0"].astype(float).to_numpy()
    grace_compare = delong_roc_test(y, prob, grace_prob)

    with_cs_features = CORE12 + ["cardiogenic_shock"]
    cs_pred = nested_oof_predictions(data, with_cs_features)
    cs_prob = cs_pred["probabilities"]
    with_cs = system_at_threshold(y, cs_prob, SCREENING_THRESHOLD)
    with_cs["auc"] = float(roc_auc_score(y, cs_prob))
    with_cs["brier"] = float(brier_score_loss(y, cs_prob))
    with_cs["feature_importance"] = cs_pred["feature_importance"]

    tradeoff = []
    for threshold in [YOUDEN_REFERENCE_THRESHOLD, 0.10, 0.08, 0.05]:
        tradeoff.append(system_at_threshold(y, prob, threshold))

    results = {
        "cohort": {"n": int(len(data)), "deaths": int(y.sum()), "survivors": int(len(data) - y.sum())},
        "main": main,
        "grace_comparison": grace_compare,
        "sensitivity_analysis": {
            "main_12_features": {
                "system_sensitivity": main["system"]["sensitivity"],
                "high_ppv": main["tiers"]["high"]["ppv"],
                "auc": main["auc"],
            },
            "with_cardiogenic_shock_13_features": {
                "system_sensitivity": with_cs["system"]["sensitivity"],
                "high_ppv": with_cs["tiers"]["high"]["ppv"],
                "auc": with_cs["auc"],
                "system": with_cs["system"],
                "tiers": with_cs["tiers"],
            },
        },
        "threshold_tradeoff": tradeoff,
        "missingness": missingness(data),
        "shock_crosstabs": shock_crosstabs(data),
        "oof_predictions": {
            "patient_id": data["patient_id"].tolist(),
            "y_true": y.tolist(),
            "model_probability": prob.tolist(),
            "grace_2_0": grace_prob.tolist(),
        },
    }
    results["guardrail_checks"] = guardrail_checks(results)

    if write_json:
        ANALYSIS_RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with ANALYSIS_RESULTS_PATH.open("w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=_json_default)
    return results


if __name__ == "__main__":
    run_analysis(write_json=True)
