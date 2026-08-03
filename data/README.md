# Data provenance

## cohort.csv

- Source: Makassar ACS Registry (single-center, de-identified).
- N = 1,817 eligible patients after exclusion; outcome = in-hospital
  all-cause mortality (209 events, 11.5%).
- **Killip IV backfill applied (definitional consistency):** Killip class IV
  corresponds to cardiogenic shock by definition, therefore
  `cardiogenic_shock = 1` for all 279 Killip IV patients (46 records updated:
  45 from 0 to 1, 1 from missing to 1; 165 records reclassified by
  definition). Post-backfill counts: cardiogenic shock 422, shock on arrival
  278, both 278, cardiogenic shock without shock on arrival 144, shock on
  arrival without cardiogenic shock 0.
- Consequence for modeling: `cardiogenic_shock` must never enter the model
  (look-ahead: the flag can be recorded after admission). Only
  `shock_on_arrival` is admission-time.
- Immutable input. Do not modify or re-derive.

## grace_scores.csv

- GRACE 2.0 in-hospital mortality scores computed on the same 1,817-patient
  cohort (patient_id + grace_2_0).
- Used only as the clinical comparator (AUC, DeLong comparison).
