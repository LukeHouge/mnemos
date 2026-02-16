# CI, Agents, and Branch Protection

How CI health checks, Cursor Cloud Agents, and GitHub branch protection work together.

## CI Workflows

Two GitHub Actions workflows run on pull requests targeting `main`:

| Workflow | File | Jobs |
|----------|------|------|
| **CI** | `.github/workflows/ci.yml` | Lint and Type Check, Run Tests |
| **Check TODOs** | `.github/workflows/todos.yml` | Scan for new TODO/FIXME/XXX comments |

### CI Job Details

- **Ruff lint** — catches unused imports, style violations, banned patterns
- **Ruff format** — verifies code formatting matches project standard
- **Pyright** — static type checking on all `app/` code
- **pytest** — unit tests with coverage report
- **Structural lint** — enforces architecture layer rules (Routes -> Services -> Models)

## Cursor Cloud Agent Capabilities

Cursor Cloud Agents run in ephemeral VMs with a GitHub App installation token (`ghs_*`). The token is auto-provisioned by the Cursor GitHub App — no manual configuration required.

### Agent Permission Matrix

| Operation | Permission | Works? |
|-----------|-----------|--------|
| Push code | `contents: write` | Yes |
| Read PRs, issues, CI runs | `metadata: read` | Yes |
| View CI logs | `actions: read` | Yes |
| Merge PRs | `contents: write` | Yes (if branch rules allow) |
| Mark PR ready for review | GraphQL | Yes |
| Create / update PRs | `pull_requests: write` | No — platform handles |
| Comment on PRs | `issues: write` | No — platform handles |
| Create reviews | `pull_requests: write` | No — platform handles |

### Agent vs Platform

The agent and the Cursor platform are separate systems with different credentials:

- **Agent** (this VM): Limited token. Pushes code, reads CI, can merge if allowed.
- **Platform** (Cursor servers): Full GitHub App permissions. Creates PRs, posts comments, creates issues as `app/cursor`.

When you @mention the Cursor bot on a PR comment:

```
You @mention cursor on a PR comment
    → GitHub webhook → Cursor Platform (full permissions)
    → Platform spins up Cloud Agent VM (limited token)
    → Agent does work (reads code, edits, pushes, reads CI)
    → Agent output returns to Cursor Platform
    → Platform posts the reply comment (its own credentials)
```

The agent never directly comments on PRs. The platform proxies the response.

### Key `gh` Commands for CI Monitoring

```bash
gh pr checks <pr-number>               # Quick pass/fail overview
gh run list --branch <branch>           # List CI runs for a branch
gh run view <run-id> --json jobs        # Structured job results
gh run view <run-id> --log              # Full CI logs
```

## Branch Protection (REQUIRED for Enterprise)

Without branch protection, agents (and anyone with push access) can merge PRs without review. This must be locked down.

### Recommended Settings for `main`

Configure via GitHub → Settings → Branches → Add branch protection rule (or Rulesets):

**Rule pattern:** `main`

| Setting | Value | Why |
|---------|-------|-----|
| **Require a pull request before merging** | Enabled | No direct pushes to main |
| **Required approving reviews** | 1 (or more) | Human must approve before merge |
| **Dismiss stale PR reviews** | Enabled | New pushes invalidate old approvals |
| **Require review from code owners** | Enabled (if CODEOWNERS exists) | Domain experts must approve |
| **Require status checks to pass** | Enabled | CI must be green before merge |
| **Required status checks** | `Lint and Type Check`, `Run Tests` | Both CI jobs must pass |
| **Require branches to be up to date** | Enabled | Branch must be current with main |
| **Do not allow bypassing** | Enabled | Applies to admins and apps too |
| **Restrict who can push** | Optional | Limit direct push to specific teams |

### What This Prevents

With these rules, the agent **cannot**:

- Merge a PR without human approval (blocked by required reviews)
- Merge a PR with failing CI (blocked by required status checks)
- Mark a PR as reviewed/approved (token lacks `pull_requests: write`)
- Push directly to main (blocked by require-PR rule)

The agent **can still**:

- Push to feature branches (necessary for its job)
- Read CI results and iterate on fixes
- Run `gh pr ready` (but the PR still needs human approval to merge)

### Setup via GitHub CLI (Admin Required)

If you have admin access, you can configure branch protection via the API:

```bash
gh api repos/OWNER/REPO/branches/main/protection \
  -X PUT \
  -f 'required_status_checks[strict]=true' \
  -f 'required_status_checks[contexts][]=Lint and Type Check' \
  -f 'required_status_checks[contexts][]=Run Tests' \
  -f 'required_pull_request_reviews[required_approving_review_count]=1' \
  -f 'required_pull_request_reviews[dismiss_stale_reviews]=true' \
  -f 'enforce_admins=true' \
  -F 'restrictions=null'
```

Or use **GitHub Rulesets** (recommended for organizations) for more granular control including specific bypass lists.

### CODEOWNERS (Optional)

Add a `CODEOWNERS` file to require specific reviewers for specific paths:

```
# Default owners for everything
* @LukeHouge

# Backend requires backend team review
/backend/ @LukeHouge
```

## Testing the @cursor Mention Workflow

To test the agent's ability to respond to PR comments:

1. Open a PR (or use an existing one)
2. Leave a comment tagging the bot, e.g.: `@cursor update the PR description with an architecture diagram`
3. The Cursor platform will spin up a cloud agent session
4. The agent does its work and pushes any code changes
5. The platform posts the agent's response as a comment

This flow exercises the full loop: webhook → agent → platform → comment reply.
