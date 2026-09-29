#!/bin/sh
# Regenerate the hash-pinned requirement lockfiles.
#
#   requirements.lock      runtime dependencies
#   requirements-dev.lock  runtime + the `dev` extra
#
# Output is deterministic for a given pyproject.toml, so re-running without
# changing dependencies produces byte-identical files (idempotent).
#
# Usage: scripts/lock.sh
# Requires: uv on PATH (https://docs.astral.sh/uv/)

set -eu

usage() {
    cat <<'EOF'
Usage: scripts/lock.sh

Regenerate requirements.lock and requirements-dev.lock from pyproject.toml
using `uv pip compile --generate-hashes`. Safe to run repeatedly.
EOF
}

case ${1:-} in
    -h | --help)
        usage
        exit 0
        ;;
    '') ;;
    *)
        printf 'ERROR: unexpected argument: %s\n\n' "$1" >&2
        usage >&2
        exit 2
        ;;
esac

# Resolve the repository root from this script's location so the script works
# from any working directory.
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

cd "$REPO_ROOT"

if [ ! -f "$REPO_ROOT/pyproject.toml" ]; then
    printf 'ERROR: pyproject.toml not found in %s\n' "$REPO_ROOT" >&2
    exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
    printf 'ERROR: required command not found: uv\n' >&2
    printf 'Install it from https://docs.astral.sh/uv/\n' >&2
    exit 127
fi

printf '==> Compiling runtime requirements -> requirements.lock\n'
uv pip compile pyproject.toml --generate-hashes -o requirements.lock

printf '\n==> Compiling dev requirements -> requirements-dev.lock\n'
uv pip compile pyproject.toml --extra dev --generate-hashes -o requirements-dev.lock

printf '\nWrote:\n  %s\n  %s\n' \
    "$REPO_ROOT/requirements.lock" \
    "$REPO_ROOT/requirements-dev.lock"
