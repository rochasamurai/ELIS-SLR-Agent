"""Policy check for model-agnostic active agent identifiers."""

from __future__ import annotations
from pathlib import Path

from elis.agent_id import contains_provider_token, legacy_to_canonical_map

CURRENT_PE_FILE = Path("CURRENT_PE.md")
PLAN_FILE = Path("ELIS_MultiAgent_Implementation_Plan_v1_8_3.md")
RUNTIME_FILE = Path("docs/openclaw/openclaw_sanitised.json")
AGENTS_FILE = Path("AGENTS.md")
ACTIVE_ID_TOKENS = [
    "infra-impl-a",
    "infra-val-b",
    "infra-impl-b",
    "infra-val-a",
    "prog-impl-a",
    "prog-impl-b",
    "prog-val-a",
    "prog-val-b",
    "harvest-impl-a",
    "harvest-val-b",
    "screen-impl-b",
    "screen-val-a",
    "extract-impl-a",
    "extract-val-b",
    "synth-impl-b",
    "synth-val-a",
    "prisma-impl-b",
    "prisma-val-a",
]


def _ensure_file(path: Path, violations: list[str]) -> str:
    if not path.exists():
        violations.append(f"Required active file missing: {path}")
        return ""
    return path.read_text(encoding="utf-8")


def _check_current_pe(violations: list[str]) -> None:
    text = _ensure_file(CURRENT_PE_FILE, violations)
    if not text:
        return
    required = ["infra-impl-a", "infra-val-b", "infra-impl-b", "infra-val-a"]
    for token in required:
        if token not in text:
            violations.append(
                f"{CURRENT_PE_FILE}: expected active id {token!r} not found."
            )
    active_prefixes = ("| PE-INFRA-SLR-04 ", "| PE-INFRA-SLR-05 ")
    for line in text.splitlines():
        if line.startswith(active_prefixes):
            for part in line.split():
                if "-impl-" in part or "-val-" in part:
                    cleaned = part.strip("|`")
                    if contains_provider_token(cleaned):
                        violations.append(
                            f"{CURRENT_PE_FILE}: active registry entry "
                            f"{cleaned!r} is model-coupled."
                        )


def _section(text: str, title: str) -> str:
    marker = f"#### {title}"
    if marker not in text:
        return ""
    tail = text.split(marker, 1)[1]
    return tail.split("#### ", 1)[0]


def _check_plan(violations: list[str]) -> None:
    text = _ensure_file(PLAN_FILE, violations)
    if not text:
        return
    for title, required in [
        (
            "PE-INFRA-SLR-04 · Model-Agnostic Agent Naming Governance",
            ["infra-impl-a", "infra-val-b"],
        ),
        (
            "PE-INFRA-SLR-05 · Gate 2 Auto-Merge Alignment",
            ["infra-impl-b", "infra-val-a"],
        ),
    ]:
        section = _section(text, title)
        if not section:
            violations.append(f"{PLAN_FILE}: missing section {title!r}.")
            continue
        for token in required:
            if token not in section:
                violations.append(
                    f"{PLAN_FILE}: expected token {token!r} " f"not found in {title!r}."
                )
        for line in section.splitlines():
            stripped = line.strip()
            if not (
                stripped.startswith("| Implementer |")
                or stripped.startswith("| Validator |")
            ):
                continue
            for word in stripped.replace("`", " ").split():
                if ("-impl-" in word or "-val-" in word) and contains_provider_token(
                    word
                ):
                    violations.append(
                        f"{PLAN_FILE}: active section {title!r} "
                        f"still contains {word!r}."
                    )


def _check_runtime(violations: list[str]) -> None:
    text = _ensure_file(RUNTIME_FILE, violations)
    if not text:
        return
    for token in ACTIVE_ID_TOKENS:
        if token not in text:
            violations.append(
                f"{RUNTIME_FILE}: expected runtime id {token!r} not found."
            )
    for word in text.replace('"', " ").replace(",", " ").split():
        if ("-impl-" in word or "-val-" in word) and contains_provider_token(word):
            violations.append(
                f"{RUNTIME_FILE}: runtime agent id {word!r} is model-coupled."
            )


def _check_agents(violations: list[str]) -> None:
    text = _ensure_file(AGENTS_FILE, violations)
    if not text:
        return
    section = text.split("## 14) Role-Based Agent Surface Normalisation", 1)
    if len(section) != 2:
        violations.append(f"{AGENTS_FILE}: section 14 missing.")
        return
    body = section[1]
    for token in ["infra-impl-a", "infra-impl-b", "infra-val-a", "infra-val-b"]:
        if token not in body:
            violations.append(
                f"{AGENTS_FILE}: expected canonical token {token!r} "
                "not found in section 14."
            )
    for word in body.replace("`", " ").split():
        if ("-impl-" in word or "-val-" in word) and contains_provider_token(word):
            violations.append(
                f"{AGENTS_FILE}: section 14 contains model-coupled id {word!r}."
            )


def policy_violations(paths: list[Path] | None = None) -> list[str]:
    violations: list[str] = []
    for old_id, new_id in legacy_to_canonical_map().items():
        if contains_provider_token(new_id):
            violations.append(
                f"Canonical id {new_id!r} still contains a provider token."
            )

    if paths is not None:
        for path in paths:
            text = _ensure_file(path, violations)
            if not text:
                continue
            for word in text.replace("`", " ").replace('"', " ").split():
                if ("-impl-" in word or "-val-" in word) and contains_provider_token(
                    word
                ):
                    violations.append(
                        f"{path}: active agent id {word!r} is model-coupled."
                    )
        return violations

    _check_current_pe(violations)
    _check_plan(violations)
    _check_runtime(violations)
    _check_agents(violations)
    return violations


def main() -> int:
    violations = policy_violations()
    if violations:
        print("FAIL: model-coupled naming remains in active agent-id surfaces")
        for item in violations:
            print(f"- {item}")
        return 1
    print("PASS: active agent-id surfaces use model-agnostic naming")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
