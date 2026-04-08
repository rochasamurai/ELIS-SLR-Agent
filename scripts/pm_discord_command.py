"""PE-AUTO-08 Discord loop command handler for the PM Agent."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys
from dataclasses import asdict, dataclass


DEFAULT_CONTROL = {
    "paused": False,
    "updated_at": "",
    "updated_by": "",
    "reason": "",
}
DEFAULT_CONTROL_PATH = pathlib.Path("config/pm_loop_control.json")


@dataclass(frozen=True)
class LoopControl:
    paused: bool
    updated_at: str
    updated_by: str
    reason: str


@dataclass(frozen=True)
class CommandResult:
    command: str
    message: str
    label_to_apply: str
    pause_loop: bool
    force_merge: bool
    audit_entry_required: bool
    control: LoopControl

    def as_dict(self) -> dict[str, object]:
        return {
            "command": self.command,
            "message": self.message,
            "label_to_apply": self.label_to_apply,
            "pause_loop": self.pause_loop,
            "force_merge": self.force_merge,
            "audit_entry_required": self.audit_entry_required,
            "control": asdict(self.control),
        }


class CommandError(RuntimeError):
    """Raised when a Discord command cannot be handled safely."""


def load_loop_control(path: pathlib.Path) -> LoopControl:
    if not path.exists():
        return LoopControl(**DEFAULT_CONTROL)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise CommandError(f"Loop control file must contain a JSON object: {path}")
    merged = {**DEFAULT_CONTROL, **data}
    return LoopControl(
        paused=bool(merged.get("paused")),
        updated_at=str(merged.get("updated_at", "")),
        updated_by=str(merged.get("updated_by", "")),
        reason=str(merged.get("reason", "")),
    )


def write_loop_control(path: pathlib.Path, control: LoopControl) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(control), indent=2) + "\n", encoding="utf-8")


def _timestamp() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat()


def _updated_control(
    *,
    paused: bool,
    actor: str,
    reason: str,
) -> LoopControl:
    return LoopControl(
        paused=paused,
        updated_at=_timestamp(),
        updated_by=actor,
        reason=reason,
    )


def handle_command(
    *,
    command: str,
    control: LoopControl,
    actor: str,
    pr_number: int | None = None,
    reason: str = "",
) -> CommandResult:
    normalised = command.strip().lower()
    if normalised == "pause":
        updated = _updated_control(
            paused=True,
            actor=actor,
            reason=reason or "PO paused the autonomous loop.",
        )
        return CommandResult(
            command="pause",
            message="Loop paused. Sequencer will stop after the current PE.",
            label_to_apply="",
            pause_loop=True,
            force_merge=False,
            audit_entry_required=False,
            control=updated,
        )
    if normalised == "resume":
        updated = _updated_control(
            paused=False,
            actor=actor,
            reason=reason or "PO resumed the autonomous loop.",
        )
        return CommandResult(
            command="resume",
            message="Loop resumed. Sequencer may advance on the next eligible trigger.",
            label_to_apply="",
            pause_loop=False,
            force_merge=False,
            audit_entry_required=False,
            control=updated,
        )
    if normalised == "veto":
        if pr_number is None:
            raise CommandError("veto command requires --pr-number")
        updated = _updated_control(
            paused=True,
            actor=actor,
            reason=reason or f"PO veto applied on PR #{pr_number}.",
        )
        return CommandResult(
            command="veto",
            message=(
                f"PM veto applied to PR #{pr_number}. Added `pm-review-required` "
                "and paused the sequencer."
            ),
            label_to_apply="pm-review-required",
            pause_loop=True,
            force_merge=False,
            audit_entry_required=False,
            control=updated,
        )
    if normalised == "override-pass":
        if pr_number is None:
            raise CommandError("override-pass command requires --pr-number")
        return CommandResult(
            command="override-pass",
            message=(
                f"PO override recorded for PR #{pr_number}. Force-merge may proceed "
                "only with a mandatory audit entry in LESSONS_LEARNED.md."
            ),
            label_to_apply="",
            pause_loop=control.paused,
            force_merge=True,
            audit_entry_required=True,
            control=control,
        )
    raise CommandError(f"Unsupported Discord command: {command}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Handle PM Discord loop commands that mutate automation state."
    )
    parser.add_argument(
        "--command",
        required=True,
        choices=["pause", "resume", "veto", "override-pass"],
    )
    parser.add_argument(
        "--control-file",
        default=str(DEFAULT_CONTROL_PATH),
        help="Path to the loop control JSON file.",
    )
    parser.add_argument(
        "--actor",
        default="PO",
        help="Actor issuing the command.",
    )
    parser.add_argument(
        "--pr-number",
        type=int,
        help="PR number for veto / override-pass commands.",
    )
    parser.add_argument(
        "--reason",
        default="",
        help="Optional reason to record in loop control state.",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Persist control-file updates for pause/resume/veto commands.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of plain text.",
    )
    args = parser.parse_args()

    try:
        control_path = pathlib.Path(args.control_file)
        control = load_loop_control(control_path)
        result = handle_command(
            command=args.command,
            control=control,
            actor=args.actor,
            pr_number=args.pr_number,
            reason=args.reason,
        )
        if args.write and args.command in {"pause", "resume", "veto"}:
            write_loop_control(control_path, result.control)
        if args.json:
            print(json.dumps(result.as_dict(), indent=2))
        else:
            print(result.message)
        return 0
    except (CommandError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
