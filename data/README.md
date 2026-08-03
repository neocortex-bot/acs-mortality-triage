# Data provenance

## cohort.csv

- Source: Makassar ACS Registry (single-center, de-identified).
- N = 1,817 eligible patients after exclusion; outcome = in-hospital
  all-cause mortality (209 events, 11.5%).
- **Killip IV backfill applied (definitional consistency):** Killip class IV
  corresponds to cardiogenic shock by definition, therefore
  `cardiogenic_shock = 1` for all 279 Killip IV patients (46 records updated:
  45 from 0 to 1, 1 from missing to 1; 165 records reclassified by
  definition). Single anchor for admission-time shock: **Killip IV = 279**
  (103 deaths, 36.9%). `shock_on_arrival` (278) is the IGD-time binary
  instantiation of the same construct: 278 of the 279 Killip IV patients had
  the flag; the 1 remaining patient had Killip IV recorded without it (timing
  artifact). Post-backfill counts: cardiogenic shock 422, of which 143 were
  recorded without Killip class IV (death rate 56.6%) - the post-admission
  look-ahead component. Shock on arrival without cardiogenic shock = 0.
- Consequence for modeling: `cardiogenic_shock` must never enter the model
  (look-ahead: the flag can be recorded after admission). Only
  `shock_on_arrival` is admission-time.
- eGFR backfill applied after source review: `egfr_igd` was derived with the
  CKD-EPI 2021 creatinine equation when `kreatinin_igd`, age, and sex were
  present but the eGFR field was empty. Validation against recorded eGFR values
  showed median derived/recorded ratio 1.000 and 99.7% within +/-10%. The
  Supabase source database was backfilled for 154 rows, including excluded
  patients, with 0 remaining source rows eligible for derivation. The cohort
  CSV was synchronized for 112 eligible cohort rows with 0 input mismatches and
  exactly 112 changed lines. Ten cohort patients remain missing eGFR because
  creatinine is unavailable. Scripts: `scripts/backfill_egfr_supabase.py` and
  `scripts/sync_egfr_csv.py`.
- Immutable input. Do not modify or re-derive.

## grace_scores.csv

- GRACE 2.0 in-hospital mortality scores computed on the same 1,817-patient
  cohort (patient_id + grace_2_0).
- Used only as the clinical comparator (AUC, DeLong comparison).
