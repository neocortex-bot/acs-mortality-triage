# AGENTS.md — Project Conventions & Methodology

This file encodes the accumulated methodology and writing conventions for this
project. Any agent (Codex, Claude Code, or other AI coding assistant) working
in this repository MUST read and follow it. It is the distilled transfer of the
author's working skills:

- writing stack: paper-submission, academic-draft-generator, humanize-writing
  (Academic English Prose mode), paper-humanizer-id
- data science stack: clinical-ml-prediction-modeling, thesis-model-pipeline
- knowledge base: tesis-s2

## 1. Scientific non-negotiables (hard rules, never break)

1. **Look-ahead bias is forbidden.** `cardiogenic_shock` must NEVER enter the
   prediction model: 143/422 patients with cardiogenic shock had no Killip
   class IV, i.e. the shock record was made without an admission-time anchor
   and can reflect documentation after admission. The admission-time anchor is
   Killip class IV (and its IGD-time binary instantiation `shock_on_arrival`).
   The ONLY place cardiogenic shock may appear is the sensitivity analysis
   (see section 3), where it demonstrates look-ahead inflation.
2. **Killip class IV = cardiogenic shock by definition.** The dataset has been
   backfilled so that `cardiogenic_shock = 1` for all 279 Killip IV patients
   (165 reclassified by definition, 46 records changed). Never "correct" this
   back to 0; it is definitional consistency, not a data error. Document it,
   do not argue it.
3. **No feature-selection leakage.** Never rank/select features on the full
   dataset (e.g., mutual information on all labels) and then cross-validate.
   Features are pre-specified by clinical domain knowledge (12 routine
   admission parameters); the threshold and tier split are pre-registered.
4. **No threshold/tier optimization on evaluation data.** Threshold 0.08 and
   the 25/50/25 tier split are fixed a priori. The Youden index (0.1513) is a
   REFERENCE threshold only, reported in Methods + Supplementary, never used
   for flagging.
5. **All reported metrics come from pooled out-of-fold predictions** (nested
   5x3 cross-validation, random_state=42). Never report training metrics as
   evidence. If a training-vs-OOF gap exists, report it as an overfitting
   signal.
6. **EPV >= 10 preferred.** Events per variable = flagged deaths / number of
   predictors. If below 10, state it as a limitation, do not hide it.
7. **External validation disclaimer is mandatory.** Single-center,
   retrospective, internal validation only. "External validation pending" must
   appear in the manuscript and README.
8. **Advisory framing only.** The system provides risk stratification to
   support, not replace, clinical judgment. Never write "the system assigns
   the patient to ICU"; write "HIGH RISK, consider ICU". All decisions remain
   with the treating physician. Clinical implications are limited to the
   referral center (ICU/HCU/ward allocation); district/network deployment is
   hypothetical and requires external validation.

## 2. Canonical numbers (source of truth — reproduce these EXACTLY)

Cohort: N = 1,817 ACS patients, 209 in-hospital deaths (11.5%), 1,608
survivors. Model: Random Forest (n_estimators=500, max_depth=6,
min_samples_leaf=5, random_state=42, n_jobs=-1) on 12 pre-specified features
(CORE12), median imputation, outer 5-fold StratifiedKFold (shuffle=True,
random_state=42), inner 3-fold for the Youden reference (estimated, not used
for flagging). Fixed screening threshold 0.08.

| Metric | Value |
|---|---|
| Stage 1 flagged | 691 (38.0%); 173 deaths, 518 survivors |
| Stage 1 sensitivity / specificity | 82.8% / 67.8% |
| Stage 1 PPV / NPV | 25.0% / 96.8% (CM 173/518/36/1090) |
| Stage 1 OOF AUC / Brier | 0.842 / 0.080 |
| GRACE 2.0 AUC (same cohort) | 0.816; Delta AUC 0.025 (DeLong p = 0.026, 95% CI 0.003-0.048) |
| HIGH tier (top 25% of flagged) | n = 172, deaths = 87, PPV = 50.6% |
| INTERMEDIATE tier (25-75%) | n = 345, deaths = 71, PPV = 20.6% |
| LOW tier (bottom 25%) | n = 174, deaths = 15, PPV = 8.6% |
| Full system (HIGH + INT escalated) | CM 158/359/51/1249 (FP = 517 escalated - 158 deaths; CM sums to 1,817) |
| System sensitivity / specificity / accuracy | 75.6% / 77.7% / 77.4% |
| System PPV / NPV | 30.6% / 96.1%; escalated 517 (28.5%) |
| Missed deaths | 51 (36 not flagged + 15 LOW tier) |
| Calibration (OOF, threshold-independent) | slope 1.088, CITL 0.017, O:E 1.015, ECE 0.018 |
| Combined system AUC | 0.842 (single-stage: equals Stage 1 AUC) |

Killip/shock cross-tabs (single anchor: Killip IV = cardiogenic shock at
presentation): Killip IV = 279 (103 deaths, 36.9%); cardiogenic shock = 422
(43.6%); CS without Killip IV = 143 (81 deaths, 56.6%) = records made after
admission (the look-ahead component). `shock_on_arrival` (278) is the IGD-time
instantiation of Killip IV (278 of the 279; the 1 remaining patient had Killip
IV recorded without the flag - a documentation-timing artifact, not a distinct
clinical concept). SOA without CS = 0. Do NOT present SOA and Killip IV as two
parallel constructs; mention SOA once, for backfill transparency only.

Missingness (12 model variables): eGFR 6.7% highest; complete case count and
any-of-12 proportion must be recomputed and reported.

If any script produces numbers that differ from the table above, the script is
wrong. Fix the script, do not "update" the canonical numbers.

## 3. Sensitivity analysis (look-ahead demonstration)

Three rows, all at threshold 0.08 with identical protocol:

1. Main (naive, 12 features): system sens 75.6%, HIGH PPV 50.6%.
2. With cardiogenic shock (13 features): sensitivity MUST rise (look-ahead
   inflation). Report the inflated numbers and explain: the flag can be
   recorded after admission, so this is the bias that the naive model avoids.
3. Report explicitly: "cardiogenic shock was not used in the main model to
   avoid look-ahead bias; including it inflates apparent performance."

## 4. Writing conventions (manuscript and README)

1. American English, IJC-compliant format: word count <= 5,000 (including
   table text), structured abstract <= 350 words, keywords <= 5, introduction
   <= 4 paragraphs, tables <= 6, figures <= 6, Vancouver references < 30,
   1.5 spacing, A4, 2.5 cm margins, Times New Roman 12 pt, .docx, anonymous
   body (double-blind) with separate title page (running title <= 16 chars +
   total word count).
2. **Zero em dashes** in prose. Audit with `grep -n '—'`. Replace with comma,
   colon, semicolon, period, or parentheses. Only exception: em dashes inside
   actual publication titles in the reference list.
3. **Never mention** "non-echo", "non-echocardiographic", LVEF, TAPSE, LVOT
   VTI, or any echocardiography parameter. The model uses 12 routine
   parameters; echocardiography is out of scope. The score is a local
   complement to GRACE.
4. **No iteration/delta language**: no "unlike earlier analyses", "in
   contrast to previous versions", "we improved". This study stands alone.
5. **Clinical-oriented, not ML slop**: explain the clinical significance of
   predictors (e.g., eGFR/urea reflect perfusion, Killip class reflects heart
   failure severity), not just "feature importance 0.152".
6. **Honest reporting**:
   - Overall sensitivity (75.6% = 158/209) is the primary metric; the
     capture rate among flagged deaths (158/173 = 91.3%) is secondary with
     the denominator stated.
   - Missed deaths (51 = 28.2% of deaths) are stated explicitly.
   - Confusion matrix must sum to N (1,817).
   - Calibration reported as slope, calibration-in-the-large, O:E ratio, and
     ECE (not Brier alone).
   - GRACE comparison: computed on the SAME cohort, report Delta AUC + p +
     CI. Frame as complementary decision support; GRACE is validated in
     millions of patients, do not claim superiority.
   - Missing data table per variable + complete-case proportion.
7. **Anti-AI writing** (humanize-writing, Academic English Prose mode):
   - No significance inflation ("pivotal", "groundbreaking", "underscores").
   - No AI vocabulary clusters (delve, robust, seamless, comprehensive,
     nuanced, multifaceted, harness, leverage...).
   - No copula avoidance ("serves as" -> "is"), no superficial -ing phrases
     ("highlighting...", "underscoring...").
   - Vary sentence length (10-word declaratives mixed with 30-word
     compounds); start some sentences with introductory clauses.
   - Decisive claims, not hedges; no "It is important to note that...".
   - No "This study demonstrates that..." crutch in every section.
   - Audit with detect-ai-patterns.py: fewer than 5 hits.
8. **References**: Vancouver, numbered by first appearance, in-text citations
   mandatory. ONLY the verified list in the build brief may be used. Never
   invent references.

## 5. Figures (publication quality)

- 300 DPI minimum PNG, self-contained (interpretable without the caption),
  consistent color palette: #2c3e50 (dark), #3498db (blue), #e74c3c (red),
  #27ae60 (green), #e67e22 (orange), #f39c12 (yellow).
- Font: labels 11-14 pt, annotations 8-10 pt, nothing below 7 pt.
- Every figure embeds its key numbers (AUC, PPV, n) directly.
- Required figures: ROC (model vs GRACE), calibration (reliability) diagram,
  tier allocation, referral-center monitoring flow, threshold trade-off,
  decision curve analysis.

## 6. Notebook conventions

- The notebook is the self-explanatory deliverable: markdown narrative cells
  that tell the full story (background -> cohort -> methods -> results ->
  limitations -> TRIPOD+AI checklist), code cells that reproduce every number.
- EXECUTE the notebook before committing. Never commit stale outputs (the
  .ipynb stores outputs in JSON; edited code with old outputs is a classic
  failure).
- No f-strings with nested quotes in cells (JSON escaping breaks execution);
  use .ljust() for aligned tables.
- Table 1 (baseline characteristics) splits by outcome (survived vs died)
  with p-values: Welch t-test for continuous, chi-square for categorical;
  Killip class is ordinal/categorical, never mean +/- SD with a t-test.
- Final code cell writes results/model_dictionary.json: machine-readable
  cohort, performance, clinical impact, feature importance, and limitations
  for downstream consumers.

## 7. Repository hygiene (this repo is judged)

- Clean structure: README.md, data/ (with provenance README), src/ (modular,
  typed), scripts/ (run_all), notebooks/, figures/, results/, manuscript/,
  requirements.txt, LICENSE, .gitignore.
- Deterministic everywhere: random_state=42, fixed seeds, fixed fold splits.
- No scratch files, no revision history cruft, no stale artifacts. If a file
  is not part of the deliverable, it does not belong in the repo.
- README must stand alone: what, why, how, results table, how to reproduce,
  limitations, license.

## 8. Data provenance (data/README.md must state)

- data/cohort.csv = Makassar ACS registry, de-identified, N = 1,817 eligible
  patients after exclusion, with the Killip IV -> cardiogenic shock backfill
  applied (definitional consistency: Killip class IV corresponds to
  cardiogenic shock; 46 records updated; cardiogenic shock total 422).
- data/grace_scores.csv = GRACE 2.0 in-hospital mortality scores computed on
  the same cohort.
- No patient identifiers. Do not re-derive or modify these files; treat them
  as immutable inputs.
