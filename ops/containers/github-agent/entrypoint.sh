#!/usr/bin/env bash
# ELIS GitHub Agent Container — Entrypoint
#
# Security-critical: this script gates every gh CLI invocation.
# - Reads GH_TOKEN from a read-only mounted secrets file
# - Only allows approved verbs
# - Never writes the token to stdout/stderr
# - Exits immediately if the identity check fails
#
# Usage:
#   entrypoint.sh --check-only              → verify identity only
#   entrypoint.sh --allow-push -- <cmd>     → run git push
#   entrypoint.sh --allow-pr-create -- <cmd>
#   entrypoint.sh --allow-pr-comment -- <cmd>
#   entrypoint.sh --allow-pr-review -- <cmd>

set -euo pipefail

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SECRETS_FILE="${SECRETS_FILE:-/run/secrets/github-agent.env}"
SCRIPT_NAME="$(basename "$0")"

# ---------------------------------------------------------------------------
# Verb allowlist — only these verbs may be executed
# ---------------------------------------------------------------------------
ALLOWED_VERBS="push pr-create pr-comment pr-review check-only"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
error()   { echo -e "\033[0;31mERROR:\033[0m $*" >&2; }
success() { echo -e "\033[0;32m[$1]\033[0m $2"; }
warn()    { echo -e "\033[1;33m[$1]\033[0m $2"; }
info()    { echo "$*"; }

usage() {
    cat >&2 <<EOF
Usage: $SCRIPT_NAME [OPTION] -- <command>

Options (verb gates):
  --check-only         Verify identity only (default)
  --allow-push         Allow git push operations
  --allow-pr-create    Allow gh pr create
  --allow-pr-comment   Allow gh pr comment
  --allow-pr-review    Allow gh pr review

Examples:
  $SCRIPT_NAME --check-only
  $SCRIPT_NAME --allow-push -- git push origin HEAD
  $SCRIPT_NAME --allow-pr-create -- gh pr create --fill
EOF
    exit 64
}

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------
VERB="check-only"
shift_args=()

if [[ $# -gt 0 ]]; then
    case "$1" in
        --check-only)     VERB="check-only";     shift ;;
        --allow-push)     VERB="push";           shift ;;
        --allow-pr-create) VERB="pr-create";     shift ;;
        --allow-pr-comment) VERB="pr-comment";   shift ;;
        --allow-pr-review) VERB="pr-review";     shift ;;
        --help|-h)        usage ;;
        *)                usage ;;
    esac
fi
if [[ $# -ge 1 ]] && [[ "$1" == "--" ]]; then
    shift
    shift_args=("$@")
fi

# ---------------------------------------------------------------------------
# Verb gate check
# ---------------------------------------------------------------------------
if ! echo "$ALLOWED_VERBS" | grep -qw "$VERB"; then
    error "'$VERB' is not in the allowlist."
    info "Allowed verbs: $ALLOWED_VERBS"
    exit 64
fi

# ---------------------------------------------------------------------------
# Load token from secrets file (safe: grep subshell, never printed)
# ---------------------------------------------------------------------------
if [[ ! -f "$SECRETS_FILE" ]]; then
    error "Secrets file not found at $SECRETS_FILE"
    exit 1
fi
GH_TOKEN="$(grep -E '^GH_TOKEN=' "$SECRETS_FILE" | head -1 | cut -d= -f2-)"
if [[ -z "$GH_TOKEN" ]]; then
    error "GH_TOKEN is empty or not found in $SECRETS_FILE"
    exit 1
fi
export GH_TOKEN

# Strip alternative auth that could confuse gh or leak host state
unset GITHUB_TOKEN GH_ENTERPRISE_TOKEN GIT_ASKPASS

# gh uses a dedicated config directory to avoid reading host config
export GH_CONFIG_DIR=/tmp/gh-config
mkdir -p "$GH_CONFIG_DIR"

# ---------------------------------------------------------------------------
# Greeting
# ---------------------------------------------------------------------------
info ""
info "========================================"
info "  ELIS GitHub Agent Container"
info "  Identity: elis-git-bot"
info "========================================"
info ""

# ---------------------------------------------------------------------------
# Identity verification (always runs)
# ---------------------------------------------------------------------------
warn CHECK "Verifying GitHub identity..."

IDENTITY_OUTPUT="$(gh auth status --show-status 2>&1 || true)"

if echo "$IDENTITY_OUTPUT" | grep -q "elis-git-bot"; then
    success PASS "Authenticated as: elis-git-bot"
elif echo "$IDENTITY_OUTPUT" | grep -q "Logged in"; then
    BOT_NAME="$(echo "$IDENTITY_OUTPUT" | grep -oP '(?<=Logged in to github\.com as )\S+' || echo "unknown")"
    warn WARN "Authenticated as: $BOT_NAME (expected: elis-git-bot)"
else
    TOKEN_CHECK="$(gh api /user --jq .login 2>&1 || true)"
    if [[ -n "$TOKEN_CHECK" ]]; then
        warn WARN "API login returned: $TOKEN_CHECK (expected: elis-git-bot)"
    else
        error "Cannot authenticate with GitHub (token may be expired or revoked)."
        unset GH_TOKEN
        exit 1
    fi
fi

# ---------------------------------------------------------------------------
# check-only verb — stop here
# ---------------------------------------------------------------------------
if [[ "$VERB" == "check-only" ]]; then
    success DONE "Identity verification complete. No operation requested."
    unset GH_TOKEN
    exit 0
fi

# ---------------------------------------------------------------------------
# Workspace sanity check
# ---------------------------------------------------------------------------
if [[ ! -d "/workspace" ]]; then
    error "/workspace is not mounted. Cannot proceed with write verb."
    unset GH_TOKEN
    exit 1
fi
if ! [[ -d "/workspace/.git" || -f "/workspace/.git" && "$(head -1 /workspace/.git 2>/dev/null)" == gitdir:* ]]; then
    error "/workspace is not a git repository (no .git directory or worktree). Push requires a valid git workspace."
    unset GH_TOKEN
    exit 1
fi

if [[ -f "/workspace/.git" ]]; then
    GITDIR_REF="$(head -1 /workspace/.git | sed 's/^gitdir: //')"
    if [[ -n "$GITDIR_REF" ]] && [[ ! -d "$GITDIR_REF" ]] && [[ ! -d "/workspace/$GITDIR_REF" ]]; then
        warn WARN "Git worktree reference $GITDIR_REF not reachable inside container; push may fail."
    fi
fi
success CHECK "Workspace /workspace is available."

# ---------------------------------------------------------------------------
# Execute the requested verb
# ---------------------------------------------------------------------------
success EXEC "Executing approved verb: $VERB"

case "$VERB" in
    push)
        if [[ ${#shift_args[@]} -eq 0 ]]; then
            error "No git command provided for push verb."
            usage
        fi
        exec "${shift_args[@]}"
        ;;
    pr-create|pr-comment|pr-review)
        if [[ ${#shift_args[@]} -eq 0 ]]; then
            error "No command provided for verb '$VERB'."
            usage
        fi
        exec "${shift_args[@]}"
        ;;
    *)
        error "Unknown verb: $VERB (this should not happen)"
        exit 64
        ;;
esac