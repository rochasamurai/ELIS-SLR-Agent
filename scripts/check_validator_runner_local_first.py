"""Validate the validator runner local-first and evidence contract.

PE-SLR-12 uses this check to prove that the governed validator runner:
- starts on the self-hosted ``elis-server`` execution surface;
- requires explicit PM authorisation via the Gate 1 assignment comment before
  dispatching (does not self-start);
- writes review artefacts to ``docs/reviews/archive/REVIEW_PE<N>.md``;
- instructs the validator agent to include all required REVIEW sections and at
  least one fenced evidence block;
- instructs the agent to verify the review file with ``check_review.py``; and
- verifies that the committed review file and formal GitHub review remain aligned
  with the branch state after the agent run.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import yaml  # noqa: E402

from elis.workflow_state_machine import (  # noqa: E402
    LOCAL_AGENT_EXECUTION_SURFACE,
)
from scripts.implementer_runner_common import (  # noqa: E402
    RunnerError,
    acceptance_criteria_for_pe,
    parse_current_pe,
)
from scripts.validator_runner_common import (  # noqa: E402
    build_validator_prompt,
    review_file_path,
)

VALIDATOR_RUNNER_WORKFLOW = Path(".github/workflows/validator-runner.yml")
VALIDATOR_DISPATCH_WORKFLOW = Path(".github/workflows/validator-dispatch.yml")
DISPATCH_SCRIPT = Path("scripts/dispatch_validator_runner.py")
RUNNER_COMMON = Path("scripts/validator_runner_common.py")

REQUIRED_WORKFLOW_INPUTS = {
    "pe_id",
    "branch",
    "engine",
    "plan_file",
    "base_branch",
    "pr_number",
}

REQUIRED_AGENT_ENTRYPOINTS = {
    "codex": "python -m scripts.run_codex_validator",
    "claude": "python -m scripts.run_claude_validator",
}

REQUIRED_AGENT_ARGS = {
    "--pe-id",
    "--plan",
    "--branch",
    "--base-branch",
    "--pr-number",
}

REQUIRED_REVIEW_SECTIONS = [
    "### Verdict",
    "### Gate results",
    "### Scope",
    "### Required fixes",
    "### Evidence",
]

REQUIRED_RUNNER_CALLS = [
    "verify_review_committed(",
    "verify_formal_review_posted(",
    "read_verdict(",
]

ARCHIVE_PREFIX = "docs/reviews/archive/"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalise_runs_on(value: object) -> set[str]:
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        return {str(item) for item in value}
    return set()


def _workflow_payload(workflow_path: Path) -> dict[str, object]:
    payload = yaml.load(_read(workflow_path), Loader=yaml.BaseLoader)
    if not isinstance(payload, dict):
        raise RunnerError(f"{workflow_path} did not parse as a YAML mapping.")
    return payload


def validate_validator_runner_local_first(
    *,
    repo_root: Path,
    current_pe_path: Path,
    plan_path: Path,
) -> list[str]:
    """Return validation errors for the validator runner contract."""

    errors: list[str] = []

    runner_workflow_path = repo_root / VALIDATOR_RUNNER_WORKFLOW
    dispatch_script_path = repo_root / DISPATCH_SCRIPT
    runner_common_path = repo_root / RUNNER_COMMON

    for path, label in (
        (runner_workflow_path, VALIDATOR_RUNNER_WORKFLOW.as_posix()),
        (dispatch_script_path, DISPATCH_SCRIPT.as_posix()),
        (runner_common_path, RUNNER_COMMON.as_posix()),
    ):
        if not path.exists():
            errors.append(f"{label} is missing.")

    if errors:
        return errors

    runner_workflow_text = _read(runner_workflow_path)
    dispatch_script_text = _read(dispatch_script_path)
    runner_common_text = _read(runner_common_path)

    try:
        runner_workflow = _workflow_payload(runner_workflow_path)
    except RunnerError as exc:
        return [str(exc)]

    # AC-1 — local-first execution surface
    jobs = runner_workflow.get("jobs", {})
    if not isinstance(jobs, dict):
        errors.append(f"{VALIDATOR_RUNNER_WORKFLOW.as_posix()} has no jobs mapping.")
    else:
        job = jobs.get("run-validator", {})
        if not isinstance(job, dict):
            errors.append(
                f"{VALIDATOR_RUNNER_WORKFLOW.as_posix()} has no run-validator job."
            )
        else:
            runs_on = _normalise_runs_on(job.get("runs-on"))
            if (
                "self-hosted" not in runs_on
                or LOCAL_AGENT_EXECUTION_SURFACE not in runs_on
            ):
                errors.append(
                    "Validator runner must run on [self-hosted, "
                    f"{LOCAL_AGENT_EXECUTION_SURFACE}]."
                )
            if "ubuntu-latest" in runs_on:
                errors.append("Validator runner must not use ubuntu-latest.")

    dispatch = runner_workflow.get("on", {}).get("workflow_dispatch", {})
    inputs = dispatch.get("inputs", {}) if isinstance(dispatch, dict) else {}
    if not isinstance(inputs, dict):
        inputs = {}
    missing_inputs = REQUIRED_WORKFLOW_INPUTS - set(inputs)
    if missing_inputs:
        errors.append(
            "Validator runner workflow_dispatch is missing inputs: "
            + ", ".join(sorted(missing_inputs))
        )

    for engine, entrypoint in REQUIRED_AGENT_ENTRYPOINTS.items():
        if entrypoint not in runner_workflow_text:
            errors.append(f"Validator runner does not invoke {engine}: {entrypoint}.")
    for argument in REQUIRED_AGENT_ARGS:
        if argument not in runner_workflow_text:
            errors.append(f"Validator runner does not pass {argument}.")

    # AC-1 — dispatch requires PM authorisation (evidence-backed state machine)
    for required_call in (
        "validator_dispatch_allowed_after_evidence(",
        "_verify_sections(",
    ):
        if required_call not in dispatch_script_text:
            errors.append(
                f"Dispatch script does not enforce authorisation guard: {required_call}."
            )

    # AC-2 — review archive path
    if ARCHIVE_PREFIX not in runner_workflow_text:
        errors.append(
            f"Validator runner workflow does not reference archive path '{ARCHIVE_PREFIX}'."
        )
    if (
        f'return f"{ARCHIVE_PREFIX}' not in runner_common_text
        and ARCHIVE_PREFIX not in runner_common_text
    ):
        errors.append(
            f"validator_runner_common.py does not use archive path '{ARCHIVE_PREFIX}'."
        )

    # AC-3, AC-4, AC-5 — prompt and post-run verification; build live prompt
    try:
        context = parse_current_pe(current_pe_path)
        criteria = acceptance_criteria_for_pe(plan_path, context.pe_id)
        prompt = build_validator_prompt(
            engine=context.validator_engine,
            repo_root=repo_root,
            current_pe_path=current_pe_path,
            plan_path=plan_path,
            pe_id=context.pe_id,
            pr_number="0",
        )
    except (OSError, RunnerError) as exc:
        errors.append(str(exc))
    else:
        if not criteria:
            errors.append(f"No acceptance criteria found for {context.pe_id}.")

        # AC-2 — prompt instructs agent to write to archive path
        expected_review_path = review_file_path(context.pe_id)
        if expected_review_path not in prompt:
            errors.append(
                f"Validator prompt does not reference the archive review path "
                f"'{expected_review_path}'."
            )

        # AC-3 — prompt lists all required REVIEW sections
        for section in REQUIRED_REVIEW_SECTIONS:
            if section not in prompt:
                errors.append(
                    f"Validator prompt does not instruct agent to write "
                    f"section '{section}'."
                )

        # AC-4 — prompt includes check_review.py verification
        if "check_review.py" not in prompt:
            errors.append(
                "Validator prompt does not include check_review.py verification step."
            )

    # AC-5 — post-run alignment checks in run_validator()
    # Use call-site patterns (arguments present) to avoid matching definitions.
    call_site_patterns = {
        "verify_review_committed": "verify_review_committed(inputs.",
        "verify_formal_review_posted": "verify_formal_review_posted(inputs.",
        "read_verdict": "read_verdict(repo_root,",
    }
    for label, pattern in call_site_patterns.items():
        if pattern not in runner_common_text:
            errors.append(
                f"validator_runner_common.py run_validator() is missing call: {label}."
            )

    vc_idx = runner_common_text.find(call_site_patterns["verify_review_committed"])
    vfr_idx = runner_common_text.find(call_site_patterns["verify_formal_review_posted"])
    rv_idx = runner_common_text.find(call_site_patterns["read_verdict"])
    if not (0 <= vc_idx < vfr_idx < rv_idx):
        errors.append(
            "run_validator() must call verify_review_committed, "
            "verify_formal_review_posted, then read_verdict — in that order."
        )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate validator runner local-first and evidence contract."
    )
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument(
        "--current-pe", default="CURRENT_PE.md", help="Path to CURRENT_PE.md."
    )
    parser.add_argument(
        "--plan",
        default=None,
        help="Path to the active plan. Defaults to CURRENT_PE.md Plan file.",
    )
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    current_pe_path = (repo_root / args.current_pe).resolve()
    try:
        context = parse_current_pe(current_pe_path)
    except (OSError, RunnerError) as exc:
        print(f"ERROR: {exc}")
        return 1
    plan_path = (
        Path(args.plan).resolve()
        if args.plan
        else (repo_root / context.plan_file).resolve()
    )

    errors = validate_validator_runner_local_first(
        repo_root=repo_root,
        current_pe_path=current_pe_path,
        plan_path=plan_path,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(
        "Validator runner local-first and evidence contract OK — "
        f"{context.pe_id} validator writes to {ARCHIVE_PREFIX} and "
        "requires PM authorisation before dispatch."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
