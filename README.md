# coder

Software engineer for your repos. Fixes bugs, builds features, refactors, writes and fixes tests, and opens pull
requests: each job in its own git worktree and `coder/<job>` branch, stopping at the PR. It never merges, never
pushes your default branch and never force-pushes.

An agent for [hq](https://github.com/Ying-Kai-Liao/hq): a specialist that runs in Claude Code with its own memory,
skills and tools, on your own Mac.

```
hq install Ying-Kai-Liao/hq-coder
```

## Start it

coder runs as one long-lived session that takes jobs one at a time (a job that arrives mid-job is queued). Start it
whichever way you work; all three are the same session:

```
hq live start coder          # picks: Orca if running, else tmux, else this terminal
hq live start coder orca     # an Orca tab you can watch and take over
hq live start coder tmux     # a tmux session: tmux attach -t hq-coder
cd ~/hq/agents/coder && hq coder    # this terminal
```

It never starts a second session where one already runs. In Orca or tmux it also takes jobs from your chats (its
Discord channel, Telegram, Slack) and from `hq ask coder "…"`, which returns at once; `hq ask --wait <id>` shows its
answers. (`tools/start.py` does the same as `hq live start coder` on older hq versions.) The first start asks Claude Code to trust coder's folder
once. One-off jobs work too: `hq coder "fix the failing date test in <repo>"`.

Then type a job, or send one from another hq agent. It answers with what changed, the tests it ran, and the PR link.

## What it needs

`git` and the GitHub CLI logged in (`gh auth login`). It runs your project's own install and test commands in the
worktree. It warns once per project when the default branch has no branch protection.

## Credits

Its method links nine skills from [pstack](https://github.com/michael-denyer/pstack-claude) (MIT, Michael Denyer's
Claude Code port of Lauren Tan's pstack): `tdd`, `deslop`, `fix-ci`, `get-pr-comments` and five principles. They are
fetched at a pinned commit on install (`skills.json`), not copied here. The pstack plugin itself is not needed.

`hq install` shows what it may do on your Mac (permissions, tools, services) before keeping it. Its memory and data
stay yours; updating it (`hq update coder`) never touches them.
