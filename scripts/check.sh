#!/bin/sh
# Quality gate for alberto-research.
#
# Runs the same checks as CI, in the same order, and stops at the first
# failure so the earliest useful error is the one on screen.
#
# Usage:
#   scripts/check.sh [command ...]
#
# Commands (default: all):
#   lint        ruff check
#   format      ruff format --check
#   type        mypy
#   test        pytest with coverage
#   bandit      bandit security scan
#   audit       pip-audit dependency audit
#   all         every command above
#
# Flags:
#   -h, --help  show this help
#
# Works from any working directory: paths are resolved from this script.

set -eu

usage() {
    cat <<'EOF'
Usage: scripts/check.sh [command ...]

Run the alberto-research quality gate. With no arguments every command runs.

Commands:
  lint        ruff check
  format      ruff format --check
  type        mypy
  test        pytest with coverage
  bandit      bandit security scan (B501 skipped: documented accepted risk)
  audit       pip-audit dependency audit
  all         every command above

Options:
  -h, --help  show this help and exit

Examples:
  scripts/check.sh lint type
  scripts/check.sh all
EOF
}

# Resolve the repository root from this script's location, following symlinks
# and tolerating invocation through a relative path.
script_path=$0
while [ -L "$script_path" ]; do
    link_target=$(readlink "$script_path")
    case $link_target in
        /*) script_path=$link_target ;;
        *) script_path=$(dirname "$script_path")/$link_target ;;
    esac
done
# `cd` into $1 and print the physical path. The subshell keeps the caller's
# working directory and CDPATH untouched.
resolve_dir() (
    unset CDPATH
    cd -- "$1" || exit 1
    pwd
)

SCRIPT_DIR=$(resolve_dir "$(dirname -- "$script_path")") || {
    printf 'ERROR: cannot resolve script directory\n' >&2
    exit 1
}
REPO_ROOT=$(resolve_dir "$SCRIPT_DIR/..") || {
    printf 'ERROR: cannot resolve repository root\n' >&2
    exit 1
}

# All tooling runs from the repository root so config discovery is stable.
cd "$REPO_ROOT"

have() {
    command -v "$1" >/dev/null 2>&1
}

# Prefer the project virtualenv when it exists; fall back to PATH.
if [ -x "$REPO_ROOT/.venv/bin/ruff" ]; then
    VENV_BIN=$REPO_ROOT/.venv/bin
    PATH="$VENV_BIN:$PATH"
    export PATH
fi

step() {
    printf '\n==> %s\n' "$1"
}

require() {
    if ! have "$1"; then
        printf 'ERROR: required command not found: %s\n' "$1" >&2
        printf 'Install the dev extras: pip install -e ".[dev]"\n' >&2
        exit 127
    fi
}

run_lint() {
    require ruff
    step "ruff check"
    ruff check .
}

run_format() {
    require ruff
    step "ruff format --check"
    ruff format --check .
}

run_type() {
    require mypy
    step "mypy"
    mypy
}

run_test() {
    require pytest
    step "pytest with coverage"
    # --cov-fail-under matches the threshold enforced in CI.
    pytest \
        --cov=alberto_research \
        --cov-branch \
        --cov-report=term-missing \
        --cov-fail-under=60
}

run_bandit() {
    require bandit
    step "bandit"
    # B501 is the documented, accepted residual risk in SECURITY_AUDIT.md for
    # the opt-in shadow-library resolver. Every other finding fails the gate.
    bandit -c pyproject.toml -r src -ll -s B501
}

run_audit() {
    require pip-audit
    step "pip-audit"
    pip-audit
}

run_command() {
    case $1 in
        lint) run_lint ;;
        format) run_format ;;
        type) run_type ;;
        test) run_test ;;
        bandit) run_bandit ;;
        audit) run_audit ;;
        all)
            run_lint
            run_format
            run_type
            run_test
            run_bandit
            run_audit
            ;;
        *)
            printf 'ERROR: unknown command: %s\n\n' "$1" >&2
            usage >&2
            exit 2
            ;;
    esac
}

if [ "$#" -eq 0 ]; then
    set -- all
fi

for arg in "$@"; do
    case $arg in
        -h | --help)
            usage
            exit 0
            ;;
    esac
done

for arg in "$@"; do
    run_command "$arg"
done

printf '\nAll requested checks passed.\n'
