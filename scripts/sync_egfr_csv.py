#!/usr/bin/env python3
"""Sync data/cohort.csv with the Supabase eGFR backfill (CKD-EPI 2021).

For the 112 cohort patients whose egfr_igd was missing (but kreatinin_igd,
age, and sex were present), fill egfr_igd with the same derived value written
to Supabase by scripts/backfill_egfr_supabase.py. Verifies input consistency
(kreatinin/age/sex match the Supabase snapshot) before writing.
"""
import json
import sys

import pandas as pd

BACKUP = sys.argv[1] if len(sys.argv) > 1 else "/tmp/egfr_backfill_backup.json"
CSV = "data/cohort.csv"

backup = {p["patient_id"]: p for p in json.load(open(BACKUP))}
df = pd.read_csv(CSV)
mask = df["egfr_igd"].isna() & df["kreatinin_igd"].notna()
print(f"CSV patients missing eGFR with creatinine present: {int(mask.sum())}")

filled, mismatches = 0, 0
for pid in df.loc[mask, "patient_id"]:
    b = backup.get(pid)
    if b is None:
        print(f"  NOT in backup: {pid}")
        continue
    row = df.loc[df.patient_id == pid]
    ok = (
        abs(float(row["kreatinin_igd"].iloc[0]) - b["kreatinin_igd"]) <= 1e-9
        and abs(float(row["age_when_admission"].iloc[0]) - b["age_when_admission"]) <= 1e-9
        and row["jenis_kelamin"].iloc[0] == b["jenis_kelamin"]
    )
    if not ok:
        mismatches += 1
        print(f"  INPUT MISMATCH: {pid}")
    df.loc[df.patient_id == pid, "egfr_igd"] = b["egfr_derived"]
    filled += 1

df.to_csv(CSV, index=False)
print(f"filled: {filled} | input mismatches: {mismatches}")
print(f"eGFR missing after sync: {int(df['egfr_igd'].isna().sum())} (expect 10, no creatinine)")
print(f"creatinine missing: {int(df['kreatinin_igd'].isna().sum())} (expect 10)")
