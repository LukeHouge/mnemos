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

## Agent Boundaries (STRICT POLICY)

Regardless of what the token technically allows, agents must NEVER:

1. **NEVER merge a PR** — merging is always a human decision (`gh pr merge` is forbidden)
2. **NEVER mark a PR as ready for review** — the author decides when it's ready (`gh pr ready` is forbidden)
3. **NEVER approve or review a PR** — reviews are human-only
4. **NEVER close or reopen issues or PRs** — lifecycle decisions belong to humans
5. **NEVER push directly to `main`** — always work on feature branches

Agents SHOULD: push code to feature branches, read CI results, iterate on fixes until checks pass, and report findings. Humans decide when to approve, merge, and release.

This policy is enforced at two layers:
- **Instructions**: Agent rules in `.cursorrules`, `AGENTS.md`, and `CLAUDE.md` explicitly forbid these actions.
- **Branch protection**: GitHub branch rules block merges without human approval as a backstop (see below).

## Cursor Cloud Agent Capabilities

Cursor Cloud Agents run in ephemeral VMs with a GitHub App installation token (`ghs_*`). The token is auto-provisioned by the Cursor GitHub App — no manual configuration required.

### Agent Permission Matrix

| Operation | Permission | Technically works? | Policy |
|-----------|-----------|-------------------|--------|
| Push to feature branches | `contents: write` | Yes | Allowed |
| Read PRs, issues, CI runs | `metadata: read` | Yes | Allowed |
| View CI logs | `actions: read` | Yes | Allowed |
| Merge PRs | `contents: write` | Yes (if no branch rules) | **FORBIDDEN by policy** |
| Mark PR ready for review | GraphQL | Yes | **FORBIDDEN by policy** |
| Approve / review PRs | `pull_requests: write` | No (token lacks permission) | Forbidden |
| Create / update PRs | `pull_requests: write` | No — platform handles | N/A |
| Comment on PRs | `issues: write` | No — platform handles | N/A |
| Push to `main` | `contents: write` | Yes (if no branch rules) | **FORBIDDEN by policy** |

### Agent vs Platform

The agent and the Cursor platform are separate systems with different credentials:

- **Agent** (this VM): Limited token. Pushes code to feature branches and reads CI.
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

### Defense in Depth

Protection works at two layers:

**Layer 1 — Agent policy** (`.cursorrules`, `AGENTS.md`, `CLAUDE.md`):
Agents are instructed to never merge, mark ready, approve, or close PRs. This is the primary control and works regardless of branch rules.

**Layer 2 — Branch protection** (GitHub settings):
Even if an agent ignores instructions or a misconfigured automation tries to merge, GitHub blocks it:

- Merge without human approval → blocked by required reviews
- Merge with failing CI → blocked by required status checks
- Push directly to main → blocked by require-PR rule
- Approve own PR → blocked (token lacks `pull_requests: write`)

**What agents CAN do** (by design):

- Push to feature branches (necessary for their job)
- Read CI results and iterate on fixes
- Report findings in their output (platform posts as comments)

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

## Known Gotchas

Things discovered through testing that future agents and contributors should know:

### PR Creation

- The Cursor platform auto-creates a **draft PR** the first time a `cursor/*` branch is pushed.
- The agent token **cannot** create PRs itself (`gh pr create` returns 403).
- If a PR is merged and the same branch name is reused, the platform **will not** auto-create a second PR. You must either use a new branch name or create the PR manually via the GitHub UI.
- The agent **cannot** update PR titles or descriptions (`gh pr edit` returns 403). The platform controls PR metadata.

### PR Comments

- The agent token **cannot** post comments on PRs or issues (both REST and GraphQL return 403).
- When the @cursor bot replies to your PR comments, the **platform** posts the comment using its own credentials — the agent just produces text output.
- If you need the agent to communicate findings on a PR, it should include them in commit messages or its text output, which the platform will post.

### Merge and Lifecycle

- The agent token **can technically** merge PRs and mark them ready (via `contents: write` and GraphQL). This is why the Agent Boundaries policy exists — technical capability does not equal permission.
- Branch protection rules are the hard backstop. Without them, nothing prevents the agent from merging.
- The agent **cannot** approve PRs (token lacks `pull_requests: write`), so it cannot self-approve-and-merge even without branch protection.

### Environment

- The `ghs_*` token is a GitHub App installation token, not a personal access token. It has no OAuth scopes — permissions are defined by the GitHub App installation.
- The token is ephemeral and scoped to the session. It is embedded in the git remote URL and configured for `gh` CLI automatically.
- `CURSOR_AGENT=1` environment variable indicates the code is running in a cloud agent VM.
