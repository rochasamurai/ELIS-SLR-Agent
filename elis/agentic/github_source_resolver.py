"""
GitHub Agent Source Path Resolver

Implements the logic for determining exactly one authorized PR source path
based on defined rules and performing readiness checks.
"""

import os
from typing import List, Optional, Tuple
from pathlib import Path


class GithubSourceResolver:
    """Resolves and validates GitHub PR source paths according to defined rules."""

    def __init__(self):
        self.authorized_source_paths = [
            # These represent authorized locations for PR source paths
            # In practice, these would be configured from environment or settings
        ]

    def get_authorized_source_paths(self) -> List[str]:
        """
        Returns all authorized PR source paths for the current operation.

        Rules:
        - Must be exactly one authorized source path (FAIL CLOSED otherwise)
        - Cannot default to runtime workspace
        """
        # This method would normally read from configuration
        return self.authorized_source_paths

    def validate_source_path(self, source_path: str) -> Tuple[bool, str]:
        """
        Validates that a source path is authorized and ready for GitHub operations.

        Returns: (is_valid, reason)
        """
        if not source_path:
            return False, "No source path provided"

        # Check if path is within authorized set
        authorized_paths = self.get_authorized_source_paths()
        if source_path not in authorized_paths:
            return False, f"Source path '{source_path}' is not authorized"

        # Check if path is runtime workspace (should be blocked)
        if self._is_runtime_workspace(source_path):
            return False, "Source path cannot be GitHub Agent runtime workspace"

        # Perform readiness checks
        is_ready, check_msg = self._perform_readiness_check(source_path)
        if not is_ready:
            return False, f"Source path not ready: {check_msg}"

        return True, "Valid source path"

    def _is_runtime_workspace(self, source_path: str) -> bool:
        """Check if the source path is the GitHub Agent runtime workspace."""
        # The runtime workspace should NOT be used as PR source
        runtime_workspace = "/opt/elis/agent-worktrees/github-agent"
        return source_path == runtime_workspace

    def _perform_readiness_check(self, source_path: str) -> Tuple[bool, str]:
        """
        Performs runtime workspace readiness checks including .openclaw check.

        Returns: (is_ready, check_message)
        """
        try:
            path_obj = Path(source_path)
            if not path_obj.exists():
                return False, "Source path does not exist"

            # Check if .openclaw directory exists (required for operations)
            openclaw_dir = path_obj / ".openclaw"
            if not openclaw_dir.exists():
                return False, "Required .openclaw directory not found"

            # Check if .openclaw directory is writable
            if not os.access(openclaw_dir, os.W_OK):
                return False, ".openclaw directory is not writable"

            return True, "Ready for GitHub operations"

        except Exception as e:
            return False, f"Readiness check failed: {str(e)}"

    def resolve_single_authorised_source(self) -> Tuple[Optional[str], str]:
        """
        Resolves exactly one authorized source path or fails closed.

        Returns: (resolved_source_path, reason)
        """
        authorized_sources = self.get_authorized_source_paths()

        if len(authorized_sources) == 0:
            return None, "No authorized PR source paths found"

        if len(authorized_sources) > 1:
            return (
                None,
                f"Multiple authorized source paths found ({len(authorized_sources)}): {', '.join(authorized_sources)}. Must resolve to exactly one.",
            )

        # Single authorized source - validate it
        source_path = authorized_sources[0]
        is_valid, reason = self.validate_source_path(source_path)

        if not is_valid:
            return None, f"Single authorized source invalid: {reason}"

        return source_path, "Single authorized source resolved successfully"


# Example usage and test routines
def example_usage():
    """Example usage of the resolver."""
    resolver = GithubSourceResolver()

    # Try to resolve source path
    source, reason = resolver.resolve_single_authorised_source()

    if source:
        print(f"✓ Valid source path: {source}")
        print(f"  Reason: {reason}")
    else:
        print(f"✗ Failed to resolve source path: {reason}")


if __name__ == "__main__":
    example_usage()
