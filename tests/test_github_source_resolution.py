"""
E2E Acceptance Tests for GitHub Agent Source Path Resolution

These tests verify that the GitHub Agent correctly selects exactly one
authorized PR source path or fails closed when multiple or no valid paths exist.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from elis.agentic.github_source_resolver import GithubSourceResolver


class TestGithubSourceResolution(unittest.TestCase):
    """Test cases for GitHub source path resolution logic."""

    def setUp(self):
        """Set up test fixtures."""
        self.resolver = GithubSourceResolver()

    def test_no_authorized_sources(self):
        """Test resolution fails when no authorized sources exist."""
        with patch.object(
            self.resolver, "get_authorized_source_paths", return_value=[]
        ):
            source, reason = self.resolver.resolve_single_authorised_source()
            self.assertIsNone(source)
            self.assertIn("No authorized PR source paths found", reason)

    def test_multiple_authorized_sources(self):
        """Test resolution fails when multiple authorized sources exist."""
        with patch.object(
            self.resolver,
            "get_authorized_source_paths",
            return_value=[
                "/opt/elis/agent-worktrees/infra-impl-a",
                "/opt/elis/agent-worktrees/infra-val-b",
            ],
        ):
            source, reason = self.resolver.resolve_single_authorised_source()
            self.assertIsNone(source)
            self.assertIn("Multiple authorized source paths found", reason)

    def test_single_valid_source(self):
        """Test successful resolution of a single valid source."""
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create .openclaw directory for readiness check
            openclaw_dir = Path(tmp_dir) / ".openclaw"
            openclaw_dir.mkdir(parents=True, exist_ok=True)

            with patch.object(
                self.resolver, "get_authorized_source_paths", return_value=[tmp_dir]
            ):
                source, reason = self.resolver.resolve_single_authorised_source()
                self.assertEqual(source, tmp_dir)
                self.assertIn("Single authorized source resolved successfully", reason)

    def test_runtime_workspace_blocked(self):
        """Test that runtime workspace is blocked as PR source."""
        runtime_path = "/opt/elis/agent-worktrees/github-agent"
        with patch.object(
            self.resolver, "get_authorized_source_paths", return_value=[runtime_path]
        ):
            source, reason = self.resolver.resolve_single_authorised_source()
            self.assertIsNone(source)
            self.assertIn("runtime workspace", reason.lower())

    def test_invalid_source_path(self):
        """Test validation fails for non-existent paths."""
        with patch.object(
            self.resolver,
            "get_authorized_source_paths",
            return_value=["/non/existent/path"],
        ):
            source, reason = self.resolver.resolve_single_authorised_source()
            self.assertIsNone(source)
            self.assertIn("does not exist", reason.lower())

    def test_missing_openclaw_directory_should_fail(self):
        """Test that missing .openclaw directory causes failure (this is the intended behavior)."""
        # Create temporary directory but DON'T create .openclaw directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch.object(
                self.resolver, "get_authorized_source_paths", return_value=[tmp_dir]
            ):
                source, reason = self.resolver.resolve_single_authorised_source()
                self.assertIsNone(source)
                self.assertIn(".openclaw directory not found", reason)


def run_acceptance_tests():
    """Run all acceptance tests."""
    print("Running GitHub Agent Source Path Resolution Acceptance Tests...")

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGithubSourceResolution)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("\n✅ All acceptance tests PASSED")
        return True
    else:
        print(f"\n❌ {len(result.failures)} failures, {len(result.errors)} errors")
        return False


if __name__ == "__main__":
    run_acceptance_tests()
