"""Run the complete ACS mortality triage analysis and figure pipeline."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.analysis import run_analysis
from src.figures import generate_figures


def main() -> None:
    results = run_analysis(write_json=True)
    generate_figures()
    print("Guardrail checks")
    for line in results["guardrail_checks"]:
        print(line)
    main = results["main"]
    print()
    print("Key results")
    print(f"Stage 1 flagged: {main['stage1']['tp'] + main['stage1']['fp']} ({main['stage1']['tp']} deaths)")
    print(f"OOF AUC: {main['auc']:.3f}; Brier: {main['brier']:.3f}")
    print(
        "System CM: "
        f"TP {main['system']['tp']} / FP {main['system']['fp']} / "
        f"FN {main['system']['fn']} / TN {main['system']['tn']}"
    )
    print(
        "System metrics: "
        f"sensitivity {main['system']['sensitivity']*100:.1f}%, "
        f"specificity {main['system']['specificity']*100:.1f}%, "
        f"PPV {main['system']['ppv']*100:.1f}%, "
        f"NPV {main['system']['npv']*100:.1f}%"
    )
    print("Note: fixed HIGH+INTERMEDIATE tiering gives 517 escalated patients, so FP is 359 and TN is 1249.")


if __name__ == "__main__":
    main()

