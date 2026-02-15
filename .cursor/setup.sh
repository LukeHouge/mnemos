#!/usr/bin/env bash
# .cursor/setup.sh - Cursor Cloud Agent environment bootstrap
#
# Runs automatically when a Cursor Cloud Agent VM spins up.
# Delegates to the shared setup script used by all AI agents.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec bash "$REPO_ROOT/scripts/setup-agent-env.sh"
