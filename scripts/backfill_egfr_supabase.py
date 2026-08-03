#!/usr/bin/env python3
"""Backfill missing egfr_igd in Supabase cleaned_data using CKD-EPI 2021.

Derives eGFR = 142 * min(Scr/k,1)^a * max(Scr/k,1)^-1.200 * 0.9938^Age
              * 1.012 (if female)
  k = 0.7 (female) / 0.9 (male); a = -0.241 (female) / -0.302 (male)
from kreatinin_igd (mg/dL) + age_when_admission + jenis_kelamin, for rows
where egfr_igd IS NULL but kreatinin_igd IS NOT NULL.

The formula was validated 1:1 against recorded eGFR values in the same table
(median derived/recorded ratio 1.000; 99.6% within +/-10%).

Workflow: backup -> dry-run plan -> PATCH per patient_id -> recount verify.
Credentials come from environment (SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY) -
never hardcode secrets. Reads ~/.hermes/.env if not already exported.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
import urllib.request

BASE = os.environ.get("SUPABASE_URL", "").rstrip("/")
KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

if not BASE or not KEY:
    env_path = os.path.expanduser("~/.hermes/.env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("SUPABASE_URL="):
                    BASE = line.split("=", 1)[1].rstrip("/")
                elif line.startswith("SUPABASE_SERVICE_ROLE_KEY="):
                    KEY = line.split("=", 1)[1]
if not BASE or not KEY:
    sys.exit("Missing SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY")


def fetch(url: str, method: str = "GET", payload: dict | None = None, retries: int = 4) -> dict | list:
    data = json.dumps(payload).encode() if payload is not None else None
    for i in range(retries):
        try:
            req = urllib.request.Request(
                url, data=data, method=method,
                headers={
                    "apikey": KEY, "Authorization": f"Bearer {KEY}",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=60) as r:
                body = r.read().decode()
                return json.loads(body) if body else {}
        except Exception as e:
            if i == retries - 1:
                raise
            time.sleep(1.5 * (i + 1))


def ckd_epi_2021(scr: float, age: float, female: bool) -> float:
    k = 0.7 if female else 0.9
    a = -0.241 if female else -0.302
    g = 142 * min(scr / k, 1) ** a * max(scr / k, 1) ** -1.200 * 0.9938 ** age
    if female:
        g *= 1.012
    return round(g, 1)  # registry convention: one decimal


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="backup + plan only, no writes")
    ap.add_argument("--backup", default="/tmp/egfr_backfill_backup.json")
    ap.add_argument("--max", type=int, default=1000, help="max rows to process")
    args = ap.parse_args()

    # 1. rows missing eGFR but with creatinine
    rows = fetch(
        f"{BASE}/rest/v1/cleaned_data"
        f"?select=patient_id,egfr_igd,kreatinin_igd,age_when_admission,jenis_kelamin"
        f"&egfr_igd=is.null&kreatinin_igd=not.is.null&limit={args.max}"
    )
    rows = [r for r in rows if r.get("patient_id")]
    print(f"Target rows (egfr NULL, kreatinin present): {len(rows)}")

    # sanity: derivation inputs present
    no_age = [r["patient_id"] for r in rows if r.get("age_when_admission") is None]
    no_sex = [r["patient_id"] for r in rows if r.get("jenis_kelamin") not in ("L", "P")]
    print(f"  missing age: {len(no_age)} | missing sex: {len(no_sex)}")
    derivable = [r for r in rows if r.get("age_when_admission") is not None
                 and r.get("jenis_kelamin") in ("L", "P")]

    # 2. formula validation on recorded rows (same table)
    sample = fetch(
        f"{BASE}/rest/v1/cleaned_data"
        f"?select=patient_id,egfr_igd,kreatinin_igd,age_when_admission,jenis_kelamin"
        f"&egfr_igd=not.is.null&kreatinin_igd=not.is.null&limit=1000"
    )
    ratios, within10 = [], 0
    for r in sample:
        if r.get("egfr_igd") is None or r.get("kreatinin_igd") is None \
           or r.get("age_when_admission") is None or r.get("jenis_kelamin") not in ("L", "P"):
            continue
        d = ckd_epi_2021(r["kreatinin_igd"], r["age_when_admission"], r["jenis_kelamin"] == "P")
        if r["egfr_igd"] and d:
            ratios.append(d / r["egfr_igd"])
            within10 += abs(d / r["egfr_igd"] - 1) <= 0.10
    med = sorted(ratios)[len(ratios) // 2] if ratios else float("nan")
    print(f"Formula validation on {len(ratios)} recorded rows: median ratio {med:.4f}, "
          f"within +/-10%: {within10}/{len(ratios)} ({100 * within10 / max(len(ratios), 1):.1f}%)")
    if med < 0.95 or med > 1.05:
        sys.exit("Formula mismatch - aborting (registry eGFR is not CKD-EPI 2021)")

    # 3. derive
    plan = []
    for r in derivable:
        plan.append({
            "patient_id": r["patient_id"],
            "egfr_derived": ckd_epi_2021(r["kreatinin_igd"], r["age_when_admission"], r["jenis_kelamin"] == "P"),
            "kreatinin_igd": r["kreatinin_igd"],
            "age_when_admission": r["age_when_admission"],
            "jenis_kelamin": r["jenis_kelamin"],
            "egfr_old": r["egfr_igd"],
        })
    print(f"Rows to backfill: {len(plan)}")

    # 4. backup
    with open(args.backup, "w") as f:
        json.dump(plan, f, indent=1)
    print(f"Backup written: {args.backup}")

    if args.dry_run:
        print("DRY RUN - no writes. Sample:")
        for p in plan[:5]:
            print(f"  {p['patient_id'][:8]}... creat={p['kreatinin_igd']} age={p['age_when_admission']} "
                  f"sex={p['jenis_kelamin']} -> egfr={p['egfr_derived']}")
        return

    # 5. PATCH per row
    ok, fail = 0, []
    for i, p in enumerate(plan):
        url = f"{BASE}/rest/v1/cleaned_data?patient_id=eq.{p['patient_id']}"
        try:
            fetch(url, method="PATCH", payload={"egfr_igd": p["egfr_derived"]})
            ok += 1
        except Exception as e:
            fail.append((p["patient_id"], str(e)))
        if i % 20 == 19:
            print(f"  patched {i + 1}/{len(plan)}")
        time.sleep(0.1)
    print(f"Patched: {ok}/{len(plan)} | failures: {len(fail)}")
    for pid, err in fail[:5]:
        print(f"  FAIL {pid[:8]}: {err}")

    # 6. verify
    remaining = fetch(
        f"{BASE}/rest/v1/cleaned_data?select=count&egfr_igd=is.null&kreatinin_igd=not.is.null&limit=1"
    )
    rem = remaining[0]["count"] if remaining else "?"
    print(f"Verification - egfr NULL & kreatinin present remaining: {rem} (expect 0)")


if __name__ == "__main__":
    main()
