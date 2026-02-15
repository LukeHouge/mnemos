#!/usr/bin/env bash
# .cursor/setup.sh - Cursor Cloud Agent environment bootstrap
#
# This script runs automatically when a Cursor Cloud Agent VM spins up.
# It installs all tools and dependencies so the agent can start working
# immediately without wasting time on setup.
#
# What it installs:
#   - uv (fast Python package manager)
#   - just (command runner)
#   - Python dependencies (backend, including dev extras)

set -euo pipefail

INSTALL_DIR="$HOME/.local/bin"
mkdir -p "$INSTALL_DIR"

# Ensure ~/.local/bin is on PATH for this script and future shell sessions
export PATH="$INSTALL_DIR:$PATH"
if ! grep -q '.local/bin' "$HOME/.bashrc" 2>/dev/null; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
fi

echo "==> Installing uv..."
if ! command -v uv &>/dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
fi
echo "    uv $(uv --version)"

echo "==> Installing just..."
if ! command -v just &>/dev/null; then
    curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh \
        | bash -s -- --to "$INSTALL_DIR"
fi
echo "    just $(just --version)"

echo "==> Installing Python dependencies (backend, including dev extras)..."
cd /workspace/backend
uv sync --extra dev
echo "    Dependencies installed"

echo "==> Environment ready!"
echo "    Tools: uv, just, ruff, pyright, pytest"
echo "    Run 'just check-local' to lint + type check"
echo "    Run 'just test-local' to run unit tests"
