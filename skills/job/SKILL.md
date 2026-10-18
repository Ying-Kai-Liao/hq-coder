---
name: job
description: Run one coding job from request to pull request — project and checkout, job file, worktree and branch, install and test commands, the PR, review fixes, and cleaning up merged jobs.
---

# A job, start to PR

`<home>` is your home, `<pkg>` your package (the folder your skills are in) and `<hq>` the kernel, all in your
instructions. Never `cd` before git or gh (Claude Code asks every time, since a repo's hooks could run): git as
`git -C "<wt>" …` (`git -C "<checkout>"` only for `fetch` and `worktree add|list|remove`), gh with
`--repo <owner/repo>`, read once from `git -C "<checkout>" remote get-url origin`. Other commands may
`cd "<wt>" && …` (`cd "<wt>" && make test`).

## 1. Intake
- Read the header (agent.md, Messages). Refuse non-owner work before anything else.
- Project: the header's `project=`, else the one the request names (check `<hq>/bin/project-id --list`), else ask
  (a one-shot can't ask: report that and stop). Never the `<session project=…>` tag: that is where the session
  started.
- Checkout: `<hq>/bin/project-id --where <ID>`. None on this Mac: ask the user for the path; don't clone unasked.
  A path the request names that is no registered project: work there as project `none` (worktrees in
  `<home>/files/none/`, no project reads or notes); don't register a project yourself.
- Do the protocol's start-of-call reads for the project. Test and install commands come from `codebase.md`
  `## Commands`; if missing, find them once (README, manifest, CI config) and add them there.
- Clean up first (step 6), then name the job `<yyyymmdd>-<kebab-summary>` (`20261019-fix-login-redirect`).

## 2. Job file
Write `<home>/memory/jobs/<job>.md` now. Keep it under 40 lines; overwrite sections, don't append history.
```
job: <job>                status: active        # queued | active | waiting | pr | done | dropped
msg: <header id or "typed">   from: <from>   reply: <reply>
project: <ID>   checkout: <path>   base: <branch> @ <short sha>
worktree: <home>/files/<ID>/worktrees/<job>   branch: coder/<job>
ask: <the request, verbatim, up to 6 lines>
assumptions: - …
acceptance: - [ ] … (checkable)
plan: - [ ] …
found: - … (one line each: what you learned that the next step needs)
tests: <command> → <result>
pr: <url>
next: <the very next action>
```
`waiting` = blocked on the user (say on what in `next:`). Update after each step and before any command that
takes more than a minute.

## 3. Worktree
```
git -C "<checkout>" fetch origin
base=$(git -C "<checkout>" symbolic-ref --short refs/remotes/origin/HEAD | sed 's|^origin/||')
git -C "<checkout>" worktree add -b coder/<job> "<home>/files/<ID>/worktrees/<job>" "origin/$base"
```
Then `<pkg>/tools/protected.sh "<checkout>" "$base"`. `unprotected`, and your project notes don't say so yet: warn
in this job's report (agent.md, How you work) and add the line.

A fresh worktree has no dependencies or build output: run the project's install command in it first
(`npm ci`, `pnpm install --frozen-lockfile`, `uv sync`, …).

No `origin`: branch from the default branch; the job ends at a committed branch. `origin` not on GitHub
(`protected.sh` says no GitHub repo): branch from `origin/$base` as above and the job ends at the pushed branch.
Either way there is no PR: set `status: done`, `pr: none (branch coder/<job>)`, and say so in the report.

Parallel parts: one more worktree per part, branched off `coder/<job>`, at `…/worktrees/<job>--<part>`. Give each
subagent its path, the part's acceptance and the test command; it commits there. Merge each part branch into
`coder/<job>` yourself, run the full tests, then remove the part worktrees.

## 4. Work
Follow the Method in agent.md. Commit in small steps with messages that say why. Before the PR, run the full test
command and the real-thing check, and record both in `tests:`.

## 5. PR
```
git -C "<wt>" push -u origin coder/<job>
gh pr create --repo <owner/repo> --base "$base" --head coder/<job> --title "<what, imperative>" --body-file <file>
```
Ready for review, never `--draft`. If it still opens as a draft (a repo default), `gh pr ready <n> --repo <owner/repo>`.
Body, short: `## Why` (the ask in one or two lines), `## What changed` (files, one line each),
`## Verification` (`Ran:` commands and results, `Checked:` the real-thing check, `Not verified:` what you could not
check). Set `status: pr` and `pr:`. Report (agent.md, Report) to the reply target. Then the end-of-call writes:
session file, project notes for anything durable (a test quirk, a slow suite), decisions if any.

Review fixes ("address the review on #12"): find the job by its `pr:`, set it `active`, read the comments with
`gh pr view <n> --repo <owner/repo> --comments`, fix in the same worktree, push new commits (never force), reply with what changed.

## 6. Cleanup (at the start of every job)
For each job file with `status: pr`: `gh pr view coder/<job> --repo <owner/repo> --json state -q .state`.
MERGED or CLOSED → `git -C "<checkout>" worktree remove "<wt>"` (it refuses uncommitted changes: leave those and
say so), then delete the local branch: MERGED → `branch -D coder/<job>` (a squash merge makes `-d` refuse though
the work landed); CLOSED → `branch -d` only, and keep the branch if it refuses. Set `status: done`. Only ever
delete `coder/` branches.
