"""Project configuration for the ACS mortality triage model."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"
FIGURES_DIR = ROOT / "figures"
MANUSCRIPT_DIR = ROOT / "manuscript"

COHORT_PATH = DATA_DIR / "cohort.csv"
GRACE_PATH = DATA_DIR / "grace_scores.csv"
ANALYSIS_RESULTS_PATH = RESULTS_DIR / "analysis_results.json"
MODEL_DICTIONARY_PATH = RESULTS_DIR / "model_dictionary.json"

RANDOM_STATE = 42
OUTER_SPLITS = 5
INNER_SPLITS = 3
SCREENING_THRESHOLD = 0.08
YOUDEN_REFERENCE_THRESHOLD = 0.1513
TIER_SPLIT = (0.25, 0.50, 0.25)

CORE12 = [
    "sbp",
    "hr",
    "killip",
    "hb_igd",
    "ureum_igd",
    "egfr_igd",
    "sii_igd",
    "kalium_igd",
    "natrium_igd",
    "age_when_admission",
    "gds_igd",
    "oxygen_more_5lpm_igd",
]

RF_PARAMS = {
    "n_estimators": 500,
    "max_depth": 6,
    "min_samples_leaf": 5,
    "random_state": RANDOM_STATE,
    "n_jobs": -1,
}

PALETTE = {
    "dark": "#2c3e50",
    "blue": "#3498db",
    "red": "#e74c3c",
    "green": "#27ae60",
    "orange": "#e67e22",
    "yellow": "#f39c12",
}

CANONICAL = {
    "n": 1817,
    "deaths": 209,
    "stage1_flagged": 691,
    "stage1_deaths": 173,
    "stage1_survivors": 518,
    "tier_high_n": 172,
    "tier_high_deaths": 87,
    "tier_intermediate_n": 345,
    "tier_intermediate_deaths": 71,
    "tier_low_n": 174,
    "tier_low_deaths": 15,
    "system_tp": 158,
    "system_fp": 359,
    "system_fn": 51,
    "system_tn": 1249,
}
