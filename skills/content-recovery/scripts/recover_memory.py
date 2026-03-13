#!/usr/bin/env python3
import argparse
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

KEEP_DEFAULT = 30


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')


def memory_files(workspace: Path):
    files = []
    mem = workspace / 'MEMORY.md'
    if mem.exists():
        files.append(mem)
    mem_dir = workspace / 'memory'
    if mem_dir.exists():
        for p in sorted(mem_dir.rglob('*')):
            if p.is_file() and p.suffix.lower() in {'.md', '.json'}:
                files.append(p)
    return files


def backup(workspace: Path, keep: int):
    root = workspace / 'memory_backups'
    root.mkdir(parents=True, exist_ok=True)
    stamp = utc_stamp()
    dest = root / stamp
    dest.mkdir(parents=True, exist_ok=True)

    files = memory_files(workspace)
    manifest = []
    for src in files:
        rel = src.relative_to(workspace)
        out = dest / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, out)
        manifest.append(str(rel).replace('\\', '/'))

    (dest / 'manifest.json').write_text(json.dumps({
        'timestamp': stamp,
        'workspace': str(workspace),
        'files': manifest,
    }, indent=2), encoding='utf-8')

    # prune
    snaps = sorted([p for p in root.iterdir() if p.is_dir()])
    while len(snaps) > keep:
        old = snaps.pop(0)
        shutil.rmtree(old, ignore_errors=True)

    print(json.dumps({'ok': True, 'action': 'backup', 'timestamp': stamp, 'fileCount': len(manifest)}))


def list_backups(workspace: Path):
    root = workspace / 'memory_backups'
    if not root.exists():
        print(json.dumps({'ok': True, 'action': 'list', 'backups': []}))
        return
    data = []
    for d in sorted([p for p in root.iterdir() if p.is_dir()], reverse=True):
        mf = d / 'manifest.json'
        files = []
        if mf.exists():
            try:
                files = json.loads(mf.read_text(encoding='utf-8')).get('files', [])
            except Exception:
                files = []
        data.append({'timestamp': d.name, 'fileCount': len(files)})
    print(json.dumps({'ok': True, 'action': 'list', 'backups': data}))


def restore(workspace: Path, timestamp: str, dry_run: bool):
    src = workspace / 'memory_backups' / timestamp
    if not src.exists():
        raise SystemExit(f'Backup not found: {timestamp}')

    manifest = src / 'manifest.json'
    if not manifest.exists():
        raise SystemExit('manifest.json missing in backup')

    files = json.loads(manifest.read_text(encoding='utf-8')).get('files', [])
    plan = []
    for rel in files:
        target = workspace / rel
        plan.append({'file': rel, 'exists': target.exists(), 'action': 'overwrite' if target.exists() else 'create'})

    if dry_run:
        print(json.dumps({'ok': True, 'action': 'restore-plan', 'timestamp': timestamp, 'plan': plan}, indent=2))
        return

    for rel in files:
        src_file = src / rel
        dst_file = workspace / rel
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dst_file)

    print(json.dumps({'ok': True, 'action': 'restore', 'timestamp': timestamp, 'fileCount': len(files)}))


def main():
    ap = argparse.ArgumentParser(description='Backup/restore assistant memory files.')
    ap.add_argument('--workspace', required=True)
    sub = ap.add_subparsers(dest='cmd', required=True)

    p_b = sub.add_parser('backup')
    p_b.add_argument('--keep', type=int, default=KEEP_DEFAULT)

    sub.add_parser('list')

    p_r = sub.add_parser('restore')
    p_r.add_argument('--timestamp', required=True)
    p_r.add_argument('--dry-run', action='store_true')

    args = ap.parse_args()
    ws = Path(args.workspace).resolve()
    if not ws.exists():
        raise SystemExit(f'Workspace not found: {ws}')

    if args.cmd == 'backup':
        backup(ws, args.keep)
    elif args.cmd == 'list':
        list_backups(ws)
    elif args.cmd == 'restore':
        restore(ws, args.timestamp, args.dry_run)


if __name__ == '__main__':
    main()
