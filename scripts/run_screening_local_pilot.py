"""Run PE-SLR-03 bounded local screening pilot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from elis.screening_local_contract import (
    ScreeningWorkspaceContract,
    detect_asreview_installation,
    run_bounded_screening_pilot,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run bounded local screening pilot for a review ID."
    )
    parser.add_argument("--review-id", required=True, help="Review identifier")
    parser.add_argument(
        "--appendix-a",
        default="json_jsonl/ELIS_Appendix_A_Search_rows.json",
        help="Path to Appendix A JSON array",
    )
    parser.add_argument(
        "--record-cap",
        type=int,
        default=100,
        help="Maximum records to process in pilot run",
    )
    parser.add_argument(
        "--root",
        default="artifacts/screening",
        help="Review-scoped screening artefact root directory",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    contract = ScreeningWorkspaceContract(
        review_id=args.review_id,
        root=Path(args.root),
    )

    asreview = detect_asreview_installation()
    report = run_bounded_screening_pilot(
        contract=contract,
        appendix_a_path=Path(args.appendix_a),
        record_cap=args.record_cap,
    )

    output = {
        "asreview": asreview,
        "pilot_report": report,
        "paths": {
            "appendix_b": str(contract.appendix_b_output()),
            "report": str(contract.pilot_report()),
            "manifest": str(contract.pilot_manifest()),
        },
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
