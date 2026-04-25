"""Validate the implementer runner local-first contract.

PE-SLR-11 uses this check to prove that the governed implementer runner starts
on the self-hosted ``elis-server`` execution surface, reads ``CURRENT_PE.md`` and
the active plan before invoking the agent, and keeps PR operations behind the
handoff guard.
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
    implementer_dispatch_allowed,
)
from scripts.implementer_runner_common import (  # noqa: E402
    RunnerError,
    acceptance_criteria_for_pe,
    build_prompt,
    parse_current_pe,
)

WORKFLOW_PATH = Path(".github/workflows/implementer-runner.yml")
RUNNER_SCRIPT = Path("scripts/implementer_runner_common.py")

REQUIRED_WORKFLOW_INPUTS = {
    "pe_id",
    "branch",
    "engine",
    "plan_file",
    "base_branch",
}

REQUIRED_AGENT_ENTRYPOINTS = {
    "codex": "python scripts/run_codex_agent.py",
    "claude": "python scripts/run_claude_agent.py",
}

REQUIRED_AGENT_ARGS = {
    "--pe-id",
    "--plan",
    "--branch",
    "--base-branch",
}


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


def validate_implementer_runner_local_first(
    *,
    repo_root: Path,
    current_pe_path: Path,
    plan_path: Path,
) -> list[str]:
    """Return validation errors for the implementer runner contract."""

    errors: list[str] = []
    workflow_path = repo_root / WORKFLOW_PATH
    runner_path = repo_root / RUNNER_SCRIPT

    if not workflow_path.exists():
        return [f"{WORKFLOW_PATH.as_posix()} is missing."]
    if not runner_path.exists():
        return [f"{RUNNER_SCRIPT.as_posix()} is missing."]

    workflow_text = _read(workflow_path)
    runner_text = _read(runner_path)
    try:
        workflow = _workflow_payload(workflow_path)
    except RunnerError as exc:
        return [str(exc)]

    jobs = workflow.get("jobs", {})
    if not isinstance(jobs, dict):
        return [f"{WORKFLOW_PATH.as_posix()} has no jobs mapping."]
    job = jobs.get("run-implementer", {})
    if not isinstance(job, dict):
        return [f"{WORKFLOW_PATH.as_posix()} has no run-implementer job."]

    runs_on = _normalise_runs_on(job.get("runs-on"))
    if "self-hosted" not in runs_on or LOCAL_AGENT_EXECUTION_SURFACE not in runs_on:
        errors.append(
            "Implementer runner must run on [self-hosted, "
            f"{LOCAL_AGENT_EXECUTION_SURFACE}]."
        )
    if "ubuntu-latest" in runs_on:
        errors.append("Implementer runner must not use ubuntu-latest.")

    dispatch = workflow.get("on", {}).get("workflow_dispatch", {})
    inputs = dispatch.get("inputs", {}) if isinstance(dispatch, dict) else {}
    if not isinstance(inputs, dict):
        inputs = {}
    missing_inputs = REQUIRED_WORKFLOW_INPUTS - set(inputs)
    if missing_inputs:
        errors.append(
            "Implementer runner workflow_dispatch is missing inputs: "
            + ", ".join(sorted(missing_inputs))
        )

    for engine, entrypoint in REQUIRED_AGENT_ENTRYPOINTS.items():
        if entrypoint not in workflow_text:
            errors.append(f"Implementer runner does not invoke {engine}: {entrypoint}.")
    for argument in REQUIRED_AGENT_ARGS:
        if argument not in workflow_text:
            errors.append(f"Implementer runner does not pass {argument}.")

    if "Notify PM Agent webhook — PE started" not in workflow_text:
        errors.append("Implementer runner does not emit the PE-started webhook.")
    if '"stage": "started"' not in workflow_text:
        errors.append("Implementer runner webhook payload lacks stage=started.")

    for required_call in (
        "parse_current_pe(current_pe_path)",
        "acceptance_criteria_for_pe(plan_path, pe_id)",
        "ensure_handoff_ready_for_pr()",
        "create_draft_pr(inputs.branch, inputs.base_branch, inputs.pe_id)",
        "mark_pr_ready(inputs.branch, inputs.base_branch)",
    ):
        if required_call not in runner_text:
            errors.append(f"Runner code is missing guard/call: {required_call}.")

    handoff_guard_index = runner_text.find("ensure_handoff_ready_for_pr()")
    pr_create_index = runner_text.find(
        "create_draft_pr(inputs.branch, inputs.base_branch, inputs.pe_id)"
    )
    ready_index = runner_text.find("mark_pr_ready(inputs.branch, inputs.base_branch)")
    if not (0 <= handoff_guard_index < pr_create_index < ready_index):
        errors.append("Runner must check HANDOFF.md before PR create/ready operations.")

    try:
        context = parse_current_pe(current_pe_path)
        criteria = acceptance_criteria_for_pe(plan_path, context.pe_id)
        prompt = build_prompt(
            engine=context.implementer_engine,
            repo_root=repo_root,
            current_pe_path=current_pe_path,
            plan_path=plan_path,
            pe_id=context.pe_id,
        )
    except (OSError, RunnerError) as exc:
        errors.append(str(exc))
    else:
        if not implementer_dispatch_allowed(context.status):
            errors.append(
                f"Active PE status is {context.status!r}; implementer dispatch "
                "requires an implementing PE."
            )
        if not criteria:
            errors.append(f"No acceptance criteria found for {context.pe_id}.")
        if "=== CURRENT_PE.md ===" not in prompt:
            errors.append("Runner prompt does not include CURRENT_PE.md context.")
        if "=== ACTIVE PLAN ACCEPTANCE CRITERIA ===" not in prompt:
            errors.append("Runner prompt does not include active plan criteria.")
        if "Do not open, refresh, or ready the PR yourself." not in prompt:
            errors.append(
                "Runner prompt does not reserve PR operations for the runner."
            )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate implementer runner local-first contract."
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

    errors = validate_implementer_runner_local_first(
        repo_root=repo_root,
        current_pe_path=current_pe_path,
        plan_path=plan_path,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(
        "Implementer runner local-first contract OK - "
        f"{context.pe_id} reads CURRENT_PE.md and {plan_path.name} before agent run."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
