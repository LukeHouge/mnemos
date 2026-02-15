# Branch Protection Setup

Type checks, linting, and tests run in CI on every PR (see `.github/workflows/ci.yml`), but **they do not currently block merging**. To enforce this, you need to configure branch protection rules on GitHub.

## Setup Instructions

1. Go to **Settings > Rules > Rulesets** in your GitHub repository
2. Click **New ruleset > New branch ruleset**
3. Configure:
   - **Name**: `Require CI to pass`
   - **Enforcement status**: `Active`
   - **Target branches**: Add `Default branch` (main)
   - **Branch rules**: Check **Require status checks to pass**
     - Enable **Require branches to be up to date before merging**
     - Add these required status checks:
       - `Lint and Type Check`
       - `Run Tests`
4. Click **Create**

## What This Enforces

Once configured, PRs targeting `main` cannot be merged unless:
- **Pyright type checking** passes with zero errors
- **Ruff linting** passes with zero errors
- **Ruff format check** passes
- **All unit tests** pass

## For AI Agents (Cursor, Claude Code)

Agent instructions in `.cursorrules` and `CLAUDE.md` require running all checks before every commit and PR. Pre-commit hooks (`.pre-commit-config.yaml`) also enforce this locally. This provides defense in depth:

1. **Pre-commit hooks** catch issues at commit time
2. **Agent instructions** ensure agents run checks proactively
3. **CI status checks** catch anything that slips through
4. **Branch protection** prevents merging if CI fails
