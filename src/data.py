"""Data loading and validation."""

from __future__ import annotations

import pandas as pd

from .config import COHORT_PATH, GRACE_PATH


def load_data() -> pd.DataFrame:
    """Load cohort and GRACE scores, validating the fixed study cohort."""
    cohort = pd.read_csv(COHORT_PATH)
    grace = pd.read_csv(GRACE_PATH)

    if cohort.shape != (1817, 131):
        raise ValueError(f"Unexpected cohort shape: {cohort.shape}")
    if grace.shape[0] != 1817:
        raise ValueError(f"Unexpected GRACE row count: {grace.shape[0]}")
    if "patient_id" not in cohort or "patient_id" not in grace:
        raise ValueError("patient_id is required in both input files")
    if cohort["patient_id"].duplicated().any() or grace["patient_id"].duplicated().any():
        raise ValueError("patient_id values must be unique")
    if int(cohort["inhospital_death"].sum()) != 209:
        raise ValueError("Expected 209 in-hospital deaths")

    data = cohort.merge(grace[["patient_id", "grace_2_0"]], on="patient_id", how="left")
    if data["grace_2_0"].isna().any():
        raise ValueError("Missing GRACE score after patient_id join")
    return data

