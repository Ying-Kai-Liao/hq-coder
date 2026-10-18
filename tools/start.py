#!/usr/bin/env python3
"""start.py [orca|tmux|here] [--dry-run] — start coder's one live session, or say where it already runs.
With an hq that has bin/hq-live this is `hq live start coder`; the code below is for older ones.

  orca   a tab titled "hq coder" in Orca (orca terminal create), so you can watch it and take it over there
  tmux   a detached tmux session "hq-coder" (tmux attach -t hq-coder)
  here   this terminal (the same as: cd <coder home> && hq coder)

With no mode: orca when the orca CLI answers, else tmux when installed, else here. Every mode starts the session in
coder's home folder, so it has no project of its own; each job names its project. Never starts a second session
where one already runs (Orca tab with that title, tmux session with that name).
CODER_ORCA_WORKTREE=<selector> picks the Orca workspace the tab sits under (default: the Orca worktree that holds
coder's home, else the active one).
"""
import json, os, shlex, shutil, subprocess, sys
from pathlib import Path

TITLE, TMUX_NAME = 'hq coder', 'hq-coder'


def home():
    here = Path(__file__).resolve().parent.parent          # the package: role/ or a snapshot
    dot = here / '.home'
    if dot.is_file():
        return Path(dot.read_text().strip())
    return Path(__file__).absolute().parent.parent.parent  # agents/coder/role/tools/start.py -> agents/coder


def hq_bin():
    found = shutil.which('hq')
    if found:
        return found
    for p in (Path.home() / 'hq' / 'kernel' / 'bin' / 'hq',):
        if p.is_file():
            return str(p)
    sys.exit('start: hq is not on PATH and ~/hq/kernel/bin/hq is missing (is hq installed?)')


def orca(*args):
    r = subprocess.run(['orca', *args, '--json'], capture_output=True, text=True, timeout=30)
    try:
        d = json.loads(r.stdout)
    except ValueError:
        return None
    return d.get('result', d) if d.get('ok', True) else None


def orca_up():
    return shutil.which('orca') is not None and orca('terminal', 'list') is not None


def orca_worktree(h):
    if os.environ.get('CODER_ORCA_WORKTREE'):
        return os.environ['CODER_ORCA_WORKTREE']
    wts = (orca('worktree', 'list') or {}).get('worktrees', [])
    targets = {str(h), str(h.resolve())}
    best = ''
    for w in wts:
        p = (w.get('path') or '').rstrip('/')
        if p and any(t == p or t.startswith(p + '/') for t in targets) and len(p) > len(best):
            best = p
    return f'path:{best}' if best else 'active'


def main():
    args = [a for a in sys.argv[1:] if a != '--dry-run']
    dry = len(args) != len(sys.argv[1:])
    h, hq = home(), hq_bin()
    live = Path(os.path.realpath(hq)).parent / 'hq-live'   # the kernel's own launcher, when this hq has one
    if live.is_file():
        os.execv(str(live), [str(live), 'start', 'coder', *sys.argv[1:]])
    mode = args[0] if args else ('orca' if orca_up() else 'tmux' if shutil.which('tmux') else 'here')
    cmd = f'cd {shlex.quote(str(h))} && {shlex.quote(hq)} coder'

    if mode == 'orca':
        live = [t for t in (orca('terminal', 'list') or {}).get('terminals', []) if t.get('title') == TITLE]
        if live:
            print(f'coder already runs in Orca: {live[0]["handle"]} (orca terminal switch --terminal {live[0]["handle"]})')
            return
        where = orca_worktree(h)
        argv = ['orca', 'terminal', 'create', '--worktree', where, '--title', TITLE, '--command', cmd, '--json']
        if dry:
            print(shlex.join(argv)); return
        r = subprocess.run(argv, capture_output=True, text=True, timeout=60)
        d = json.loads(r.stdout or '{}')
        if not d.get('ok'):
            sys.exit(f'start: orca terminal create failed: {(d.get("error") or {}).get("message", r.stderr.strip())}')
        t = d['result'].get('terminal', d['result'])
        print(f'coder started in Orca: tab "{TITLE}", {t.get("handle")} (under {where})')
    elif mode == 'tmux':
        if not shutil.which('tmux'):
            sys.exit('start: tmux is not installed (brew install tmux), or use: start.py here')
        if subprocess.run(['tmux', 'has-session', '-t', TMUX_NAME], capture_output=True).returncode == 0:
            print(f'coder already runs in tmux: tmux attach -t {TMUX_NAME}'); return
        argv = ['tmux', 'new-session', '-d', '-s', TMUX_NAME, '-c', str(h), cmd]
        if dry:
            print(shlex.join(argv)); return
        subprocess.run(argv, check=True)
        print(f'coder started in tmux: tmux attach -t {TMUX_NAME}')
    elif mode == 'here':
        if dry:
            print(cmd); return
        os.chdir(h)
        os.execv(hq, [hq, 'coder'])
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main()
