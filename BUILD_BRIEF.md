# BUILD BRIEF — Fresh repository for the ACS mortality triage model (Design C, single-stage)

You are working in `/home/linuxmint/acs-mortality-triage` (fresh git repo, branch `main`, nothing committed yet except the files listed below). Your job is to build the COMPLETE, clean, publication-grade repository from scratch. The repo will be judged by a technical jury, so quality of structure, documentation, reproducibility, and honesty matter as much as the numbers.

## READ FIRST

`AGENTS.md` (repo root) is the authoritative conventions document. It contains the non-negotiable scientific rules, the canonical numbers your pipeline MUST reproduce exactly, writing conventions, figure/notebook/hygiene rules, and data provenance. Follow it throughout. This brief adds the concrete build plan and deliverables.

## Inputs already present (do NOT modify)

- `data/cohort.csv` — 1,817 patients, outcome column `inhospital_death` (209 deaths), 131 columns. Killip IV backfill already applied.
- `data/grace_scores.csv` — `patient_id`, `grace_2_0` (GRACE 2.0 in-hospital mortality score on the same cohort).
- `data/README.md`, `AGENTS.md`.

## The model (Design C — single-stage, exactly as specified)

- **Stage 1 (the only stage):** RandomForestClassifier(n_estimators=500, max_depth=6, min_samples_leaf=5, random_state=42, n_jobs=-1) on exactly these 12 features:
  `sbp, hr, killip, hb_igd, ureum_igd, egfr_igd, sii_igd, kalium_igd, natrium_igd, age_when_admission, gds_igd, oxygen_more_5lpm_igd`
- Median imputation (sklearn SimpleImputer) fitted on training folds only.
- Validation: outer StratifiedKFold(n_splits=5, shuffle=True, random_state=42) → pooled out-of-fold probabilities. Inner StratifiedKFold(n_splits=3, shuffle=True, random_state=42) on each training fold to estimate the Youden reference threshold (0.1513) — estimated, NEVER used for flagging.
- **Screening threshold: 0.08 (fixed, pre-registered).** Patients with OOF probability >= 0.08 are flagged (expect 691 flagged, 173 deaths).
- **Tiers (pre-registered 25/50/25):** within the flagged pool, rank by OOF Stage 1 probability (np.argsort, kind="mergesort", descending). HIGH = top 25% (n=172), INTERMEDIATE = next 50% (n=345), LOW = bottom 25% (n=174). Escalated = HIGH + INTERMEDIATE (n=517).
- **Guardrail — reproduce EXACTLY** (pooled OOF): tiers HIGH 172 with 87 deaths (PPV 50.6%), INT 345 with 71 deaths (20.6%), LOW 174 with 15 deaths (8.6%); full-system confusion matrix TP 158 / FP 359 / FN 51 / TN 1249 (FP = 517 escalated - 158 deaths; the matrix sums to 1,817); sensitivity 75.6% (158/209), specificity 77.7%, accuracy 77.4%, PPV 30.6%, NPV 96.1%; Stage 1 OOF AUC 0.842, Brier 0.080. If your numbers differ, your code is wrong — fix it.
- Calibration (threshold-independent, pooled OOF): logistic calibration slope 1.088, calibration-in-the-large 0.017, O:E 1.015, ECE 0.018 (10 equal-frequency bins, weighted as in `ece()`). Recompute and report.
- GRACE comparison on the same cohort: GRACE AUC 0.816; Delta AUC 0.025 with DeLong test p-value (0.026) and 95% CI (0.003-0.048). Report exactly.
- EPV: 173 flagged deaths / 12 features = 14.4 (report it; meets EPV >= 10).
- Missingness: per-variable table for the 12 model features (eGFR 6.7% expected highest), complete-case count, any-of-12 proportion (recompute).
- Killip/shock cross-tabs for the cohort description: Killip IV 279, CS 422, SOA 278, both 278, CS without SOA 144, SOA without CS 0; death rates SOA 37.1%, CS 43.6%, CS without SOA 56.2%.

## Sensitivity analysis (look-ahead demonstration)

Same protocol, threshold 0.08:
1. Main (12 features, naive): numbers above.
2. With `cardiogenic_shock` added as a 13th feature: report the inflated sensitivity/tier metrics. Guardrail: sensitivity MUST be higher than the main model (this is the look-ahead inflation the naive design avoids). Explain in the manuscript that the flag can be recorded after admission.
Never use cardiogenic_shock anywhere else.

## Threshold trade-off table (Supplementary Table S2)

- System-level metrics (flag at threshold t, tiers 25/50/25 within the flagged pool, escalated = HIGH+INT) at t = 0.1513 (Youden reference), 0.10, 0.08 (selected), 0.05: sensitivity, false positives, missed deaths, flagged n, escalated n, PPV, specificity. Guardrail row t=0.08: escalated 517, sens 75.6%, FP 359.

## Deliverables (build in this order)

1. `src/config.py` — CORE12 list, hyperparameters, threshold, tier split, paths, seeds (single source of truth for all other modules).
2. `src/data.py` — load cohort + GRACE, validate shapes (1,817 rows, 209 deaths), patient_id join.
3. `src/metrics.py` — ece(), sensitivity/specificity/accuracy/ppv/npv, confusion matrix, DeLong test (or scipy-based two-correlated-AUC test), calibration slope/CITL/O:E.
4. `src/analysis.py` — the full nested-CV single-stage pipeline above; writes `results/analysis_results.json` (ALL metrics, tiers, CM, calibration, GRACE comparison, missingness, cross-tabs, feature importances (Gini), sensitivity rows, trade-off table). Deterministic.
5. `src/figures.py` — generates ALL figures into `figures/` (300 DPI PNG, palette and rules per AGENTS.md section 5):
   - `fig1_roc.png` — Stage 1 vs GRACE ROC with AUCs and Delta AUC annotated.
   - `fig2_calibration.png` — reliability diagram with slope/CITL/O:E/ECE annotated.
   - `fig3_tiers.png` — tier allocation: n, deaths, PPV per tier (HIGH/INT/LOW) + not-flagged bar.
   - `fig4_flow.png` — referral-center monitoring allocation flow: 1,817 → 691 flagged → HIGH 172 (ICU) / INT 345 (HCU) / LOW 174 (ward) / 1,126 standard care. Advisory wording, referral center only.
   - `fig5_threshold_tradeoff.png` — sensitivity vs false positives across the trade-off table.
   - `fig6_dca.png` — decision curve analysis (model vs treat-all vs treat-none).
6. `scripts/run_all.py` — runs analysis + figures end to end, prints the guardrail checks (asserts canonical numbers), writes results.
7. `notebooks/01_analysis_walkthrough.ipynb` — SELF-EXPLANATORY, fully executed (no stale outputs). Markdown narrative + code cells that reproduce every result: background & objectives → cohort & outcomes → methods (model, CV, threshold rationale incl. Youden-as-reference, tier protocol) → results (discrimination vs GRACE, calibration, tiers, trade-off, sensitivity with-CS) → clinical interpretation at the referral center (advisory) → limitations (single-center, internal validation only, EPV, PPV bound at 11.5% prevalence) → TRIPOD+AI 2024 checklist (29 items, mapping each to its location) → `results/model_dictionary.json` writer (machine-readable cohort/performance/clinical-impact/features/limitations for downstream agents). Follow AGENTS.md section 6 (Table 1 split by outcome with p-values, Killip as categorical, .ljust() not f-strings with nested quotes, execute before commit).
8. `manuscript/acs_mortality_triage_manuscript.docx` — FRESH manuscript generated via python-docx, IJC-compliant per AGENTS.md section 4: title, structured abstract (<=350 words), keywords (<=5), Introduction (<=4 paragraphs), Methods, Results, Discussion, Limitations, Conclusion, References (Vancouver, 12 references, in-text citations by first appearance). Word count <= 5,000 including table text (count paragraphs + table cells, split on whitespace — and write the exact count into the manuscript footer/cover line "Manuscript word count: N"). Embed figures (fig1, fig2, fig3, fig4) each in a new centered paragraph after its legend; tables: Table 1 baseline by outcome with p-values, Table 2 model vs GRACE performance, Table 3 tier allocation; supplementary: Table S1 missingness, Table S2 threshold trade-off (embed fig5/fig6 as supplementary figures). Zero em dashes in prose (audit `grep -n '—'`), zero echo/echo-parameter mentions, no delta language, advisory framing, honest metrics (overall sensitivity primary, missed deaths explicit, CM sums to 1,817), calibration reported, external validation disclaimer, TRIPOD+AI mentioned. Clinical-oriented prose: explain why each predictor matters clinically.
9. `references/verified-references.md` — copy the 12 references below verbatim, mark as claim-verified.
10. `README.md` — stands alone: what/why/how, one-paragraph summary, results table (the canonical numbers), repo structure, how to reproduce (`pip install -r requirements.txt`, `python scripts/run_all.py`, `jupyter notebook`), model dictionary note, limitations, advisory disclaimer, license (MIT), data provenance pointer. Professional tone, no em dashes.
11. `requirements.txt` — pinned versions of exactly what you use (pandas, numpy, scikit-learn, matplotlib, scipy, python-docx, jupyter, nbconvert, nbformat).
12. `LICENSE` (MIT), `.gitignore` (Python + notebook cruft; keep `data/*.csv` TRACKED — they are required for reproducibility).
13. `results/model_dictionary.json` — produced by the notebook.

## Verified references (use ONLY these; never invent references; Vancouver order = first appearance)

1. Collet JP, Thiele H, Barbato E, et al. 2020 ESC Guidelines for the management of acute coronary syndromes in patients presenting without persistent ST-segment elevation. Eur Heart J. 2021;42:1289-1367.
2. Byrne RA, Rossello X, Coughlan JJ, et al. 2023 ESC Guidelines for the management of acute coronary syndromes. Eur Heart J. 2023;44:3720-3826.
3. Fox KAA, Dabbous OH, Goldberg RJ, et al. Prediction of risk of death and myocardial infarction in the six months after presentation with acute coronary syndrome: prospective multinational observational study (GRACE). BMJ. 2006;333:1091.
4. Granger CB, Goldberg RJ, Dabbous O, et al. Predictors of hospital mortality in the Global Registry of Acute Coronary Events. Arch Intern Med. 2003;163:2345-2353.
5. Killip T 3rd, Kimball JT. Treatment of myocardial infarction in a coronary care unit: a two year experience with 250 patients. Am J Cardiol. 1967;20:457-464.
6. Breiman L. Random forests. Mach Learn. 2001;45:5-32.
7. Steyerberg EW, Uno H, Ioannidis JPA, et al. Poor performance of clinical prediction models: the harm of commonly applied methods. J Clin Epidemiol. 2018;98:133-143.
8. van Smeden M, Moons KGM, de Groot JAH, et al. Sample size for binary logistic prediction models: beyond events per variable criteria. Stat Methods Med Res. 2019;28(8):2455-2474.
9. DeLong ER, DeLong DM, Clarke-Pearson DL. Comparing the areas under two or more correlated receiver operating characteristic curves: a nonparametric approach. Biometrics. 1988;44(3):837-845.
10. Collins GS, Moons KGM, Dhiman P, et al. TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods. BMJ. 2024;385:e078378.
11. Van Calster B, McLernon DJ, van Smeden M, Wynants L, Steyerberg EW. Calibration: the Achilles heel of predictive analytics. BMC Med. 2019;17:230.
12. Vickers AJ, Elkin EB. Decision curve analysis: a novel method for evaluating prediction models. Med Decis Making. 2006;26(6):565-574.

## Final steps

1. Run `scripts/run_all.py` yourself; confirm the guardrail assertions pass.
2. Execute the notebook (jupyter nbconvert --to notebook --execute) and confirm clean execution with fresh outputs.
3. Audit: zero em dashes in manuscript prose and README; no echo mentions; word count line correct; confusion matrix sums to 1,817; figures exist and are non-empty PNGs.
4. `git add` everything and commit with a clear message (e.g., "Complete ACS mortality triage repository: single-stage RF (Design C), analysis, figures, notebook, manuscript").
5. Report: the results table, the exact word count, the guardrail check results, and any deviation from this brief. Do NOT push (the orchestrator handles push). Do NOT touch anything outside this repo.
