#!/usr/bin/env bash
# scripts/setup-agent-env.sh - Shared agent environment bootstrap
#
# Installs all tools and dependencies needed to work on this repo.
# Called automatically by:
#   - Cursor Cloud Agents via .cursor/setup.sh
#   - Claude Code via .claude/settings.json SessionStart hook
#
# Can also be run manually: bash scripts/setup-agent-env.sh
#
# What it installs:
#   - uv (fast Python package manager)
#   - just (command runner)
#   - Python dependencies (backend, including dev extras)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INSTALL_DIR="$HOME/.local/bin"
mkdir -p "$INSTALL_DIR"

export PATH="$INSTALL_DIR:$HOME/.cargo/bin:$PATH"
if ! grep -q '.local/bin' "$HOME/.bashrc" 2>/dev/null; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
fi

echo "==> Installing uv..."
if ! command -v uv &>/dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$INSTALL_DIR:$HOME/.cargo/bin:$PATH"
fi
echo "    uv $(uv --version)"

echo "==> Installing just..."
if ! command -v just &>/dev/null; then
    curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh \
        | bash -s -- --to "$INSTALL_DIR"
fi
echo "    just $(just --version)"

echo "==> Installing Python dependencies (backend, including dev extras)..."
cd "$REPO_ROOT/backend"
uv sync --extra dev
echo "    Dependencies installed"

echo "==> Environment ready!"
echo "    Tools: uv, just, ruff, pyright, pytest"
echo "    Run 'just harness' to verify everything"
