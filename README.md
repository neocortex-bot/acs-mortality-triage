# ACS Mortality Triage Model

This repository contains a reproducible single-center analysis for an admission-time acute coronary syndrome mortality triage model. The model is intended for referral-center risk stratification and supports, not replaces, clinical judgment. External validation pending.

## Summary

The cohort includes 1,817 de-identified ACS admissions and 209 in-hospital deaths. A random forest model uses 12 pre-specified routine admission variables with fold-specific median imputation and pooled out-of-fold validation. The fixed screening threshold is 0.08. Patients flagged at that threshold are split into HIGH, INTERMEDIATE, and LOW tiers using a fixed 25/50/25 ranking rule. HIGH and INTERMEDIATE are escalated for closer monitoring consideration.

## Main Results

| Metric | Result |
|---|---:|
| Cohort | 1,817 patients, 209 deaths (11.5%) |
| Flagged | 682 (37.5%), with 172 deaths |
| Flagging sensitivity / specificity | 82.3% / 68.3% |
| Flagging PPV / NPV | 25.2% / 96.7% |
| OOF AUC / Brier | 0.843 / 0.080 |
| GRACE 2.0 AUC | 0.816 |
| HIGH tier | n=170, deaths=88, PPV=51.8% |
| INTERMEDIATE tier | n=341, deaths=70, PPV=20.5% |
| LOW tier | n=171, deaths=14, PPV=8.2% |
| Escalated | 511 (28.1%) |
| System confusion matrix | TP 158, FP 353, FN 51, TN 1255 |
| System sensitivity / specificity / accuracy | 75.6% / 78.0% / 77.8% |
| System PPV / NPV | 30.9% / 96.1% |
| Missed deaths | 51 of 209 (24.4%) |
| Calibration | slope 1.076, CITL 0.015, O:E 1.014, ECE 0.017 |

The fixed tier rule gives 511 escalated patients. With 158 deaths in HIGH plus INTERMEDIATE, the internally consistent false-positive count is 353 and the true-negative count is 1255.

eGFR was derived with the CKD-EPI 2021 formula when creatinine, age, and sex were present but the source eGFR field was empty. This reduced cohort eGFR missingness from 6.7% to 0.6%.

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
