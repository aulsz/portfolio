---
name: content-recovery
description: Create and recover workspace memory backups (MEMORY.md and memory/*.md) after accidental wipes, bad edits, corruption, or missing files. Use when the user asks to restore memory/content history, set backup cadence, or perform recovery drills.
---

# Content Recovery

Protect and recover memory files used by the assistant.

## Scope

- `MEMORY.md`
- `memory/*.md`
- Optional: `memory/*.json`

## Workflow

1. **Snapshot now** before any risky change.
2. **Verify latest backups** and summarize coverage.
3. **Recover safely** using preview mode first.
4. **Restore files** only after explicit confirmation.
5. **Validate** recovered content and report what changed.

## Use scripts

- Backup now:
  - `python skills/content-recovery/scripts/recover_memory.py backup --workspace <workspace-path>`
- List backups:
  - `python skills/content-recovery/scripts/recover_memory.py list --workspace <workspace-path>`
- Dry-run restore:
  - `python skills/content-recovery/scripts/recover_memory.py restore --workspace <workspace-path> --timestamp <UTCSTAMP> --dry-run`
- Restore for real:
  - `python skills/content-recovery/scripts/recover_memory.py restore --workspace <workspace-path> --timestamp <UTCSTAMP>`

## Rules

- Never overwrite current files without an explicit user “yes restore”.
- Always show restore plan first (files to overwrite/create/delete).
- Keep backups in `memory_backups/` under workspace.
- Keep at most 30 snapshots by default; prune oldest first.
- After restore, recommend running a quick integrity check and writing a postmortem note.

## Integrity checklist

- `MEMORY.md` exists and is non-empty
- at least one `memory/YYYY-MM-DD.md` exists
- no empty markdown files introduced by restore
- summarize line/file counts before vs after
