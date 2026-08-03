# ACS Mortality Triage Model

This repository contains a reproducible single-center analysis for an admission-time acute coronary syndrome mortality triage model. The model is intended for referral-center risk stratification and supports, not replaces, clinical judgment. External validation pending.

## Summary

The cohort includes 1,817 de-identified ACS admissions and 209 in-hospital deaths. A single-stage random forest uses 12 pre-specified routine admission variables with fold-specific median imputation and pooled out-of-fold validation. The fixed screening threshold is 0.08. Patients flagged at that threshold are split into HIGH, INTERMEDIATE, and LOW tiers using a fixed 25/50/25 ranking rule. HIGH and INTERMEDIATE are escalated for closer monitoring consideration.

## Main Results

| Metric | Result |
|---|---:|
| Cohort | 1,817 patients, 209 deaths (11.5%) |
| Stage 1 flagged | 691 (38.0%), with 173 deaths |
| Stage 1 sensitivity / specificity | 82.8% / 67.8% |
| Stage 1 PPV / NPV | 25.0% / 96.8% |
| OOF AUC / Brier | 0.842 / 0.080 |
| GRACE 2.0 AUC | 0.816 |
| HIGH tier | n=172, deaths=87, PPV=50.6% |
| INTERMEDIATE tier | n=345, deaths=71, PPV=20.6% |
| LOW tier | n=174, deaths=15, PPV=8.6% |
| Escalated | 517 (28.5%) |
| System confusion matrix | TP 158, FP 359, FN 51, TN 1249 |
| System sensitivity / specificity / accuracy | 75.6% / 77.7% / 77.4% |
| System PPV / NPV | 30.6% / 96.1% |
| Missed deaths | 51 of 209 (24.4%) |
| Calibration | slope 1.088, CITL 0.017, O:E 1.015, ECE 0.018 |

The fixed tier rule gives 517 escalated patients. With 158 deaths in HIGH plus INTERMEDIATE, the internally consistent false-positive count is 359 and the true-negative count is 1249.

## Repository Structure

| Path | Purpose |
|---|---|
| `data/` | Immutable cohort and GRACE score inputs with provenance notes |
| `src/` | Configuration, data loading, metrics, analysis, and figures |
| `scripts/run_all.py` | End-to-end analysis and figure runner |
| `notebooks/01_analysis_walkthrough.ipynb` | Executed narrative notebook with model dictionary writer |
| `figures/` | Publication PNG figures at 300 DPI |
| `results/` | Machine-readable analysis outputs |
| `manuscript/` | Draft manuscript in DOCX format |
| `references/` | Verified Vancouver references |

## Reproduction

```bash
pip install -r requirements.txt
python scripts/run_all.py
jupyter notebook notebooks/01_analysis_walkthrough.ipynb
```

The notebook writes `results/model_dictionary.json` for downstream systems.

## Model Variables

The 12 admission variables are systolic blood pressure, heart rate, Killip class, hemoglobin, urea, estimated glomerular filtration rate, systemic immune-inflammation index, potassium, sodium, age at admission, random glucose, and oxygen need above 5 L/min. Cardiogenic shock is excluded from the main model to avoid look-ahead bias; it appears only in the sensitivity analysis.

## Limitations

This is a single-center retrospective study with internal validation only. External validation pending. The observed 11.5% mortality prevalence bounds positive predictive value, so the model should be read as a triage support tool, not a rule for admission location. All ICU, HCU, and ward decisions remain with the treating physician.

## License

MIT. See `LICENSE`.

