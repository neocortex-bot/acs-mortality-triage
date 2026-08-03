# EXPAND BRIEF — Expand the manuscript draft to full depth (3,400-3,700 words)

Repo: `/home/linuxmint/acs-mortality-triage` (branch `main`, committed). You are
already inside it. Read `AGENTS.md` first: it is the authoritative conventions
document (scientific rules, canonical numbers, writing rules, figure rules).

## Task

The current `manuscript/acs_mortality_triage_manuscript.docx` is a complete but
compact IMRAD draft (~1,600-1,700 words). Expand it into a full-depth,
submission-ready draft of **3,400-3,700 words** (including table text), while
preserving every existing correct sentence, number, and structure. This is
EXPANSION, not rewriting: read the current docx content first, keep the
existing prose where it is good, and add the required depth section by section.

## Hard constraints (unchanged, from AGENTS.md — obey all of them)

- All numbers must come from `results/analysis_results.json` and MUST NOT
  change. Never invent or round differently. Key numbers you will use:
  N=1,817; deaths 209 (11.5%); survivors 1,608; flagged 691 (38.0%) with 173
  deaths (Stage 1 sens 82.8%, spec 67.8%, PPV 25.0%, NPV 96.8%); OOF AUC 0.842,
  Brier 0.080; GRACE AUC 0.816, Delta 0.025, DeLong p=0.026, 95% CI
  0.003-0.048; tiers HIGH n=172 deaths=87 PPV 50.6%, INT n=345 deaths=71 PPV
  20.6%, LOW n=174 deaths=15 PPV 8.6%; escalated 517 (28.5%); system CM TP 158
  / FP 359 / FN 51 / TN 1249 (sums to 1,817); system sens 75.6%, spec 77.7%,
  acc 77.4%, PPV 30.6%, NPV 96.1%; missed deaths 51 (36 not flagged + 15 LOW
  tier; 24.4% of all deaths); capture among flagged deaths 158/173 = 91.3%;
  EPV 14.4 (173/12); calibration slope 1.088, CITL 0.017, O:E 1.015, ECE 0.018;
  Youden reference 0.1513 (inner CV, reference only); trade-off at 0.1513
  (sens 60.3%, FP 195, escalated 321), 0.10 (69.9%, 298, 444), 0.08 (75.6%,
  359, 517), 0.05 (82.8%, 509, 682); with-CS sensitivity: sens 90.9%, HIGH PPV
  62.0%, AUC 0.938 (look-ahead inflation); missingness eGFR 6.7% highest,
  complete-case and any-of-12 from the JSON; Killip IV 279, CS 422, SOA 278,
  both 278, CS without SOA 144, SOA without CS 0; death rates SOA 37.1%, CS
  43.6%, CS without SOA 56.2%; feature importances from the JSON (Killip
  highest ~0.152, urea ~0.138, eGFR ~0.120, SBP ~0.090, SII ~0.090, O2 ~0.084).
- Zero em dashes in prose (audit `grep -n '—'` on the extracted text). Zero
  mention of echo/echocardiography terms. No delta/iteration language ("unlike
  earlier analyses", "we improved", "previous versions"). Advisory framing:
  HIGH/INT are "consider ICU/HCU monitoring" implications, never automated
  assignments; clinical implications limited to the referral center;
  district/network deployment is hypothetical and requires external
  validation. American English, IJC format (1.5 spacing, A4, 2.5 cm margins,
  Times New Roman 12 pt, double-blind body, separate title page info).
- Overall sensitivity (75.6% = 158/209) is the primary metric; 91.3% is
  secondary with explicit denominator. Missed deaths stated explicitly.
  Confusion matrix must sum to 1,817. Calibration reported as
  slope/CITL/O:E/ECE. GRACE framed as complementary decision support (it is
  validated in millions of patients; do not claim superiority). TRIPOD+AI
  adherence stated.
- References: the 12 verified Vancouver references in
  `references/verified-references.md`, numbered by first appearance, in-text
  citations mandatory. Do not add or remove references.

## Required depth by section (add these; keep existing correct content)

1. **Abstract** (structured, <= 350 words): keep, polish only if needed.
2. **Introduction** (<= 4 paragraphs): burden of ACS and in-hospital
   mortality; why early risk stratification matters for triage/monitoring
   allocation; existing scores (GRACE, TIMI) and their role; rationale for a
   pragmatic machine-learning score from routine admission parameters at the
   referral center; explicit study objective.
3. **Methods**, expanded into subsections:
   - Study design and setting (single-center retrospective registry cohort,
     referral center; ethics/IRB statement; TRIPOD+AI).
   - Participants and outcomes (inclusion/exclusion; N=1,817; outcome
     in-hospital all-cause mortality; note Killip IV definitional consistency:
     279 Killip IV patients, cardiogenic shock 422, shock on arrival 278).
   - Predictors (the 12 variables, each with CLINICAL significance: e.g.,
     urea/eGFR reflect renal perfusion, Killip class reflects heart failure
     severity, SII reflects inflammatory burden, oxygen need above 5 L/min
     reflects respiratory distress; all available within the first hour).
   - Missing data (per-variable table S1; median imputation within cross-
     validation folds only; complete-case and any-missing proportions).
   - Model development (random forest, hyperparameters and why: depth/leaf
     constraints to limit overfitting; EPV 14.4; pre-specified features).
   - Internal validation (nested 5x3 stratified cross-validation, pooled
     out-of-fold predictions; no feature selection or threshold tuning on
     evaluation data).
   - Screening threshold (Youden index 0.1513 computed as a reference only;
     lower thresholds examined; 0.08 selected as a clinical triage safety
     choice; trade-off table S2: 21 additional deaths captured vs 164
     additional false positives relative to the Youden reference — compute
     the exact differences from the JSON rows and state them).
   - Tier protocol (pre-registered 25/50/25 percentile split of the score
     within flagged patients; HIGH, INTERMEDIATE, LOW; escalated = HIGH +
     INTERMEDIATE; advisory implications ICU/HCU/ward at the referral
     center).
   - Comparator (GRACE 2.0 in-hospital score computed on the same cohort).
   - Statistical analysis (AUC, DeLong test for correlated ROC curves,
     calibration slope/CITL/O:E/ECE, sensitivity analysis adding
     cardiogenic shock to demonstrate look-ahead bias).
4. **Results**, expanded:
   - Baseline characteristics (Table 1: survived vs died columns with p-values;
     continuous = mean +/- SD + Welch t-test; categorical = n (%) + chi-square;
     Killip as categorical rows; include the shock cross-tabs narrative:
     SOA 37.1% vs CS 43.6% vs CS-without-SOA 56.2% death rates).
   - Missing data paragraph.
   - Discrimination (AUC 0.842 vs GRACE 0.816; Delta 0.025; DeLong p = 0.026;
     95% CI 0.003-0.048; Table 2).
   - Calibration (slope 1.088, CITL 0.017, O:E 1.015, ECE 0.018).
   - Tier allocation (Table 3: HIGH 172/87/50.6%, INT 345/71/20.6%, LOW
     174/15/8.6%, not flagged 1,126/36/3.2%; escalated 517; system CM
     158/359/51/1249; sens 75.6%, spec 77.7%, acc 77.4%, PPV 30.6%, NPV 96.1%;
     missed deaths 51 with breakdown).
   - Threshold trade-off narrative (reference the 4 rows).
   - Sensitivity analysis: including cardiogenic shock inflates sensitivity
     to 90.9% and AUC to 0.938, demonstrating the look-ahead bias that the
     main model avoids (the flag can be recorded after admission; 144 of 422
     patients with cardiogenic shock had no shock flag on arrival).
5. **Discussion**, expanded (target ~800-1,000 words):
   - Principal findings (one decisive paragraph).
   - Clinical use at the referral center (monitoring allocation ICU/HCU/ward
     as an implication for prospective evaluation; advisory, not automated).
   - Comparison with GRACE (complementary; modest Delta AUC; GRACE
     validated in millions; both are decision support).
   - The look-ahead demonstration as a methodological contribution (honest
     reporting of what including post-admission variables would do).
   - Resource-limited/district projection: explicitly hypothetical, requires
     external validation, treatment and facility paradoxes mean transfer-
     ability cannot be assumed.
   - Per-predictor clinical interpretation (renal dominance: the kidney as an
     early sensor of hypoperfusion; Killip; SII; oxygen need).
   - Limitations (single-center, retrospective, internal validation only,
     modest event count, PPV bounded by 11.5% prevalence, missing data,
     label noise, no temporal or external validation).
6. **Conclusion** (2-3 decisive sentences, no hedging).
7. **References**: unchanged (12).

## Formatting and delivery

- Keep the existing docx structure (headings, embedded figures fig1-fig6,
  tables 1-3 + S1-S2). Add Table 1 (baseline by outcome with p-values) and
  Table S1 (missingness) if not already present; if present, keep.
- After editing, rebuild the docx cleanly with python-docx (Times New Roman
  12 pt, 1.5 line spacing, A4, 2.5 cm margins, figures embedded each in a new
  centered paragraph after its legend, heading hierarchy real Word headings).
- Compute the word count deterministically: sum over all paragraphs AND all
  table cells, split on whitespace. Write "Manuscript word count: N" into the
  manuscript. Target: 3,400-3,700.
- Run `python3 scripts/audit_docx.py` and make sure it reports: word count in
  range, zero em/en dashes, no forbidden terms, no delta language, all key
  numbers present, 12 references, 6 embedded figures.
- Do NOT modify: results JSONs, src/, notebooks/, README.md, data/.
- Commit with a clear message.

## Report

Report: final word count, the audit output, the section word counts, and any
deviation from this brief. Do not push.
