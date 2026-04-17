# Git commands (quick reference)

Run these from your **repository root** unless noted. This repo ignores `.env` and `.venv`; secrets and local Python env stay off the remote by default.

## Everyday workflow

| Goal | Command |
|------|---------|
| See what changed | `git status` |
| See diffs | `git diff` (unstaged) · `git diff --staged` (staged) |
| Stage files | `git add <path>` · `git add -p` (patch hunks) · `git add -u` (update tracked only) |
| Commit | `git commit -m "Short imperative summary"` |
| Push current branch | `git push -u origin HEAD` (first time) · `git push` (after upstream set) |
| Pull and merge/rebase | `git pull` · `git pull --rebase` |

## Branches

| Goal | Command |
|------|---------|
| List branches | `git branch` · `git branch -a` (include remotes) |
| Create and switch | `git switch -c feature/name` |
| Switch branch | `git switch main` |
| Rename current branch | `git branch -m new-name` |
| Delete local branch | `git branch -d branch-name` · `-D` if not merged |
| Delete remote branch | `git push origin --delete branch-name` |

## History and inspection

| Goal | Command |
|------|---------|
| Log (compact) | `git log --oneline --graph -20` |
| Log with diffs | `git log -p -1` (last commit) |
| Who changed a line | `git blame <file>` |
| Show a commit | `git show <hash>` |

## Undo and repair (use with care)

| Goal | Command |
|------|---------|
| Unstage (keep file changes) | `git restore --staged <file>` |
| Discard local changes in file | `git restore <file>` |
| Amend last commit (message or add files) | `git commit --amend` · `git commit --amend --no-edit` |
| Undo last commit, keep changes staged | `git reset --soft HEAD~1` |
| Undo last commit, keep changes unstaged | `git reset --mixed HEAD~1` |
| Drop last commit and its changes | `git reset --hard HEAD~1` (destructive) |

If you already **pushed** the commit, prefer `git revert <hash>` for a safe history on shared branches instead of rewriting history.

## Stash

| Goal | Command |
|------|---------|
| Stash tracked changes | `git stash push -m "note"` |
| Stash including untracked | `git stash push -u -m "note"` |
| List stashes | `git stash list` |
| Apply latest stash | `git stash pop` · `git stash apply` (keep stash) |
| Drop latest stash | `git stash drop` |

## Remotes and sync

| Goal | Command |
|------|---------|
| List remotes | `git remote -v` |
| Add remote | `git remote add origin <url>` |
| Fetch without merging | `git fetch origin` |
| Prune deleted remote branches | `git fetch --prune` |

## Tags

| Goal | Command |
|------|---------|
| List tags | `git tag` |
| Create lightweight tag | `git tag v1.0.0` |
| Push tags | `git push origin v1.0.0` · `git push origin --tags` |

## Merge conflicts

1. `git status` shows conflicted files.
2. Edit files, resolve `<<<<<<<` / `=======` / `>>>>>>>` markers.
3. `git add <resolved-files>` then `git commit` (or continue rebase: `git rebase --continue`).

Abort an in-progress merge: `git merge --abort`. Abort rebase: `git rebase --abort`.

## Useful one-offs

| Goal | Command |
|------|---------|
| Clone | `git clone <url> [directory]` |
| Shallow clone (faster, limited history) | `git clone --depth 1 <url>` |
| Ignore local changes to tracked file (temporary) | `git update-index --assume-unchanged <file>` · undo: `--no-assume-unchanged` |
| Clean untracked files (dangerous) | `git clean -fd` (dry-run: `git clean -fdn`) |

## This repo

- **Do not commit** `.env` (secrets, local URLs). Share a template (e.g. `.env.example`) if you add one.
- **`__pycache__` / `.pyc`:** If they appear in `git status`, add them to `.gitignore` or adjust tooling so they are not tracked.

For a full tutorial, see [Pro Git](https://git-scm.com/book/en/v2) or `git help <command>`.
