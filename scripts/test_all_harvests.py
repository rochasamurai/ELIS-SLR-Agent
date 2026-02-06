"""
test_all_harvests.py
Runs all 9 harvest scripts with testing tier and validates JSON output.

Usage:
  python scripts/test_all_harvests.py
"""

import subprocess
import json
import sys
import os
from pathlib import Path

# Configuration
CONFIG = "config/searches/electoral_integrity_search.yml"
TIER = "testing"
OUTPUT_DIR = Path("tests/outputs")

SCRIPTS = [
    ("scopus", "scripts/scopus_harvest.py", "scopus_id"),
    ("sciencedirect", "scripts/sciencedirect_harvest.py", "sciencedirect_id"),
    ("wos", "scripts/wos_harvest.py", "wos_id"),
    ("ieee", "scripts/ieee_harvest.py", "ieee_id"),
    ("semantic_scholar", "scripts/semanticscholar_harvest.py", "s2_id"),
    ("openalex", "scripts/openalex_harvest.py", "openalex_id"),
    ("crossref", "scripts/crossref_harvest.py", "doi"),
    ("core", "scripts/core_harvest.py", "core_id"),
    ("google_scholar", "scripts/google_scholar_harvest.py", "google_scholar_id"),
]


def run_harvest(name, script, id_field):
    """Run a single harvest script and validate output."""
    output_file = OUTPUT_DIR / f"test_{name}.json"

    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}")

    # Run the harvest script
    cmd = [
        sys.executable,
        script,
        "--search-config",
        CONFIG,
        "--tier",
        TIER,
        "--output",
        str(output_file),
    ]

    result = {
        "name": name,
        "script": script,
        "status": "UNKNOWN",
        "records": 0,
        "has_id_field": False,
        "authors_issues": 0,
        "year_issues": 0,
        "error": None,
    }

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300, env=os.environ)

        if proc.returncode != 0:
            result["status"] = "FAILED"
            result["error"] = proc.stderr[:200] if proc.stderr else "Unknown error"
            print(f"  FAILED: {result['error']}")
            return result

        # Validate output file
        if not output_file.exists():
            result["status"] = "FAILED"
            result["error"] = "Output file not created"
            print("  FAILED: Output file not created")
            return result

        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        result["records"] = len(data)

        if not data:
            result["status"] = "EMPTY"
            print("  WARNING: No records returned")
            return result

        # Check for ID field
        result["has_id_field"] = any(r.get(id_field) for r in data)

        # Check for type issues
        for r in data:
            if isinstance(r.get("authors"), str):
                result["authors_issues"] += 1
            if isinstance(r.get("year"), str):
                result["year_issues"] += 1

        # Determine status
        if result["authors_issues"] > 0 or result["year_issues"] > 0:
            result["status"] = "TYPE_ISSUES"
        elif not result["has_id_field"]:
            result["status"] = "MISSING_ID"
        else:
            result["status"] = "PASSED"

        print(f"  Records: {result['records']}")
        print(f"  Has {id_field}: {'Yes' if result['has_id_field'] else 'No'}")
        print(f"  Authors as string: {result['authors_issues']}")
        print(f"  Year as string: {result['year_issues']}")
        print(f"  Status: {result['status']}")

    except subprocess.TimeoutExpired:
        result["status"] = "TIMEOUT"
        result["error"] = "Script timed out after 300s"
        print("  TIMEOUT: Script took too long")
    except json.JSONDecodeError as e:
        result["status"] = "INVALID_JSON"
        result["error"] = str(e)
        print(f"  INVALID JSON: {e}")
    except Exception as e:
        result["status"] = "ERROR"
        result["error"] = str(e)
        print(f"  ERROR: {e}")

    return result


def verify_secrets():
    """Verify all required environment variables are set."""
    print("=" * 60)
    print("Verifying Environment Variables (API Keys/Tokens)")
    print("=" * 60)
    print()

    required_secrets = [
        "SCOPUS_API_KEY",
        "SCOPUS_INST_TOKEN",
        "SCIENCEDIRECT_API_KEY",
        "SCIENCEDIRECT_INST_TOKEN",
        "WEB_OF_SCIENCE_API_KEY",
        "IEEE_EXPLORE_API_KEY",
        "SEMANTIC_SCHOLAR_API_KEY",
        "CORE_API_KEY",
        "APIFY_API_TOKEN",
        "ELIS_CONTACT",
    ]

    missing = []
    for secret in required_secrets:
        if not os.getenv(secret):
            missing.append(secret)

    if not missing:
        print("✅ All 10 required environment variables are configured")
        print()
        print("Configured:")
        for secret in required_secrets:
            print(f"  ✓ {secret}")
        print()
        print("=" * 60)
        print()
        return True
    else:
        print(f"❌ ERROR: Missing {len(missing)} required environment variable(s)")
        print()
        print("Missing:")
        for secret in missing:
            print(f"  ✗ {secret}")
        print()
        print("Please set missing variables in your environment or .env file")
        print("See: docs/REPO_HYGIENE_PLAN_2026-02-05.md (Section 12)")
        print()
        print("=" * 60)
        return False


def main():
    # Verify environment variables first
    if not verify_secrets():
        print()
        print("ABORTED: Cannot run tests without required API credentials")
        return 1

    print("=" * 60)
    print("ELIS Harvest Scripts - Local Validation")
    print("=" * 60)
    print(f"Config: {CONFIG}")
    print(f"Tier: {TIER}")
    print(f"Output: {OUTPUT_DIR}/")

    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Run all harvests
    results = []
    for name, script, id_field in SCRIPTS:
        result = run_harvest(name, script, id_field)
        results.append(result)

    # Print summary
    print("\n")
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(
        f"{'Script':<20} {'Status':<12} {'Records':<8} {'ID':<5} {'Auth':<5} {'Year':<5}"
    )
    print("-" * 60)

    passed = 0
    failed = 0

    for r in results:
        id_ok = "Yes" if r["has_id_field"] else "No"
        auth = r["authors_issues"] if r["authors_issues"] > 0 else "-"
        year = r["year_issues"] if r["year_issues"] > 0 else "-"
        print(
            f"{r['name']:<20} {r['status']:<12} {r['records']:<8} {id_ok:<5} {auth:<5} {year:<5}"
        )

        if r["status"] == "PASSED":
            passed += 1
        elif r["status"] in ("FAILED", "ERROR", "TIMEOUT", "INVALID_JSON"):
            failed += 1

    print("-" * 60)
    print(
        f"Passed: {passed}/9  |  Failed: {failed}/9  |  Type Issues: {9 - passed - failed}/9"
    )
    print("=" * 60)

    # Cleanup hint
    print(f"\nTo clean up test files: Remove-Item -Recurse {OUTPUT_DIR}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
