import pathlib

from elis import workload_placement_policy as wpp


def test_policy_declares_screening_and_lightweight_support():
    policy = wpp.DEFAULT_WORKLOAD_PLACEMENT_POLICY
    local = set(policy.local_workload_classes)
    assert "screening" in local
    assert "lightweight-support" in local


def test_docs_reference_local_first_for_screening_and_support():
    p = pathlib.Path("docs/slr/WORKLOAD_PLACEMENT_POLICY.md")
    text = p.read_text(encoding="utf8")
    assert "screening" in text
    assert "lightweight-support" in text
