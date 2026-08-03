# REBUILD BRIEF — post-eGFR-backfill rebuild (single source of truth)

Repo: `/home/linuxmint/acs-mortality-triage` (branch `main`). Read `AGENTS.md`
first. Do NOT commit (your sandbox .git is read-only); leave the tree dirty and
report.

## What happened (context, already done — do not redo)

The source data were corrected: `egfr_igd` was missing for 122 patients (6.7%)
because the lab field was not populated, although `kreatinin_igd` + age + sex
were present. eGFR was derived with the CKD-EPI 2021 formula (validated 1:1
against recorded values: median ratio 1.000, 99.7% within +/-10%) and
backfilled in BOTH the Supabase source DB (154 rows, incl. excluded patients;
verified 0 remaining) AND `data/cohort.csv` (112 cohort patients, 0 input
mismatches, exactly 112 lines changed). 10 patients without creatinine remain
missing. Files already updated and correct: `data/cohort.csv`,
`scripts/backfill_egfr_supabase.py`, `scripts/sync_egfr_csv.py`.

`python3 -m src.analysis` now FAILS its guardrail because the canonical
numbers shifted. Your job: refresh the canonical numbers, make the manuscript
fully data-driven, rebuild all artifacts, update docs, and verify.

## Task 1 — Update `src/config.py` CANONICAL (exact new values)

Replace the CANONICAL dict values (observed after backfill):

| key | old | NEW |
|---|---|---|
| stage1_flagged | 691 | **682** |
| stage1_deaths | 173 | **172** |
| stage1_survivors | 518 | **510** |
| tier_high_n | 172 | **170** |
| tier_high_deaths | 87 | **88** |
| tier_intermediate_n | 345 | **341** |
| tier_intermediate_deaths | 71 | **70** |
| tier_low_n | 174 | **171** |
| tier_low_deaths | 15 | **14** |
| system_tp | 158 | 158 (unchanged) |
| system_fp | 359 | **353** |
| system_fn | 51 | 51 (unchanged) |
| system_tn | 1249 | **1255** |

Then run `python3 -m src.analysis` until all 13 guardrails PASS. Do NOT touch
`src/analysis.py` or `src/data.py`.

## Task 2 — Make manuscript numbers data-driven (`scripts/build_artifacts.py`)

The manuscript text currently hardcodes many metrics. Refactor
`manuscript_text()` (and the notebook builder `build_notebook()`) so every
metric is interpolated from `results` (the single source of truth). The values
below are the NEW canonical numbers — use them for any f-string default or
where interpolation is impractical, but PREFER interpolation:

- Flagged 682 (37.5%), flagged deaths 172, flagged survivors 510
  (flagging sens 82.8%? recompute: 172/209 = 82.3%; spec = 510/1608 =
  31.7%? NO - recompute from results: stage1 tp=172, fp=510 -> sens
  172/209=82.3%, spec (1608-510)/1608=68.3%; use results values)
- Tiers: HIGH n=170 deaths=88 PPV=51.8%; INT n=341 deaths=70 PPV=20.5%;
  LOW n=171 deaths=14 PPV=8.2%; not flagged n=1135 deaths=37
- Escalated (HIGH+INT) = 511 (28.1%)
- System CM: TP 158 / FP 353 / FN 51 / TN 1255 (sums to 1,817)
- sens 75.6% (158/209), spec 78.0%, acc 77.8%, PPV 30.9%, NPV 96.1%
- Missed deaths 51 of 209 (24.4%): 37 not flagged + 14 LOW tier
- Flagged-death capture: 158/172 = 91.9%
- OOF AUC 0.843, Brier 0.080; GRACE AUC 0.816, delta 0.027, DeLong p 0.021
  (use results['grace_comparison'] values)
- Calibration: slope 1.076, CITL 0.015, O:E 1.014, ECE 0.017
  (use results['main']['calibration'])
- Missingness: eGFR now 0.55%; highest is ureum 1.4%, then gds ~1.2%,
  sii ~0.9%; complete-case 1,745 (96.0%); any-missing 72 (4.0%)
  (make this paragraph fully dynamic from results['missingness'])
- Threshold trade-off rows (0.1513, 0.10, 0.08, 0.05): use
  results['threshold_tradeoff'] (escalated at 0.08 = 511, not 517)
- Sensitivity with-CS: sens 90.4%, HIGH PPV 63.2%, AUC 0.938
- Discussion: "The model flagged 37.5% of patients" ; GRACE paragraph:
  "AUC 0.843 compared with GRACE 2.0 AUC 0.816 ... difference of 0.027 and
  DeLong p = 0.021" (interpolate from results)
- Abstract: update every metric (682/172; tier deaths 88/70/14 with PPV
  51.8/20.5/8.2; sens 75.6, spec 78.0, PPV 30.9, NPV 96.1; AUC 0.843;
  GRACE 0.816; calibration slope 1.076, CITL 0.015, O:E 1.014, ECE 0.017)
- Notebook markdown/code: "flagged 691 patients and captured 173" ->
  data-driven (682/172); model_dictionary 'escalated_n': 517 -> compute
  from results (high+intermediate = 511)

## Task 3 — Rebuild artifacts

1. `python3 -c "import sys; sys.path.insert(0,'scripts'); import
   build_artifacts as b; r=b.load_results(); b.build_notebook(r);
   print('wc:', b.build_manuscript(r))"` (regenerates notebook + manuscript
   + model_dictionary; do NOT run scripts/run_all.py)
2. `python3 scripts/fix_notebook_path.py` (re-adds the sys.path guard cell)
3. `jupyter nbconvert --to notebook --execute --inplace
   --ExecutePreprocessor.record_timing=False notebooks/01_analysis_walkthrough.ipynb`
4. `python3 scripts/audit_docx.py` — must show: word count in 3,400-3,700,
   zero em/en dashes, all key numbers OK, 12 references, 6 figures
5. Remove `scripts/collect_new_canonical.py` (temporary utility).

## Task 4 — Update docs

- `README.md` Main Results table: Flagged 682 (37.5%) with 172 deaths;
  flagging sens/spec 82.3%/68.3%; PPV/NPV 25.2%/96.8% (recompute from
  results if different); OOF AUC/Brier 0.843/0.080; GRACE 0.816; HIGH
  n=170 deaths=88 PPV=51.8%; INT 341/70/20.5%; LOW 171/14/8.2%;
  Escalated 511 (28.1%); CM 158/353/51/1255; sens/spec/acc 75.6/78.0/77.8;
  PPV/NPV 30.9/96.1; calibration slope 1.076, CITL 0.015, O:E 1.014,
  ECE 0.017. Add a line about the eGFR derivation (CKD-EPI 2021 backfill,
  missingness 6.7% -> 0.6%).
- `AGENTS.md` section 2 canonical table: update all numbers above;
  missingness line: eGFR 0.55% (derived via CKD-EPI 2021 from
  kreatinin_igd + age + sex; 112 backfilled in Supabase + CSV; 10 remain
  missing without creatinine); complete-case 1,745; any-missing 72.
  Update the sensitivity section numbers (with-CS sens 90.4%, HIGH PPV
  63.2%, AUC 0.938) and the trade-off mentions (escalated 511).
- `data/README.md`: add eGFR backfill section (formula, validation stats,
  Supabase 154 rows + CSV 112 rows, script names, 10 remaining).

## Constraints

- Zero em dashes in prose. No stage terminology ("single-stage", "Stage 1")
  - keep the novel one-shot framing. No mention of "Design C".
- All numbers MUST come from `results/analysis_results.json` after your
  re-run - if a metric you print differs from what you read in the JSON,
  the JSON wins; re-check.
- Do not modify: src/analysis.py, src/data.py, data/cohort.csv,
  data/grace_scores.csv, scripts/backfill_egfr_supabase.py,
  scripts/sync_egfr_csv.py.
- Do not push. Leave tree dirty.

## Report

Report: guardrail PASS count after Task 1; the exact metric values you used
per section; word count + audit output; which docs changed; any deviation.
