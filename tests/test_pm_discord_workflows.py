from __future__ import annotations

from pathlib import Path


def test_pm_arbiter_escalate_payload_mentions_po() -> None:
    workflow = Path(".github/workflows/pm-arbiter.yml").read_text(encoding="utf-8")
    assert "PM_AGENT_PO_MENTION" in workflow
    assert '"po_mention": os.environ.get("PM_AGENT_PO_MENTION", "@PO")' in workflow
    assert "[ESCALATE]" in workflow


def test_implementer_runner_notifies_started_event() -> None:
    workflow = Path(".github/workflows/implementer-runner.yml").read_text(
        encoding="utf-8"
    )
    assert "Notify PM Agent webhook — PE started" in workflow
    assert '"event": "pe-lifecycle"' in workflow
    assert '"stage": "started"' in workflow


def test_pm_discord_command_workflow_can_apply_veto_and_pause() -> None:
    workflow = Path(".github/workflows/pm-discord-command.yml").read_text(
        encoding="utf-8"
    )
    assert "pm-review-required" in workflow
    assert "config/pm_loop_control.json" in workflow
    assert "workflow_dispatch" in workflow
    assert "override-pass" in workflow
    assert "python scripts/generate_pe_status_report.py > command.txt" in workflow


def test_pm_observability_dashboard_runs_hourly_and_posts_to_discord() -> None:
    workflow = Path(".github/workflows/pm-observability-dashboard.yml").read_text(
        encoding="utf-8"
    )
    assert 'cron: "0 * * * *"' in workflow
    assert "generate_pe_status_report.py" in workflow
    assert "PM_AGENT_WEBHOOK_URL" in workflow
    assert "#pe-status" in workflow
