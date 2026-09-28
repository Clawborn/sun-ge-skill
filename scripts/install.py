#!/usr/bin/env python3
"""Install the local skill payload; Python 3.9+, standard library only."""
import argparse
import hashlib
from pathlib import Path
import shutil
import sys
import tempfile
import uuid
import zipfile

SOURCE = Path(__file__).resolve().parent.parent
PAYLOAD = ('SKILL.md', 'references', 'agents')


def snapshot(root):
    result = {}
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError('Refusing symbolic link: ' + str(path))
        if path.is_file():
            result[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
        elif not path.is_dir():
            raise ValueError('Refusing special file: ' + str(path))
    return result


def destination(args):
    if args.dest:
        return Path(args.dest).expanduser().absolute()
    bases = {
        'codex': Path.home() / '.agents' / 'skills',
        'claude': Path.home() / '.claude' / 'skills',
        'openclaw': Path.home() / '.openclaw' / 'skills',
    }
    return bases[args.agent] / 'sun-ge'


def install(dest, update=False, dry_run=False):
    # Never replace the repository, a parent of it, or a path inside it.
    resolved = dest.resolve()
    if resolved == SOURCE or SOURCE in resolved.parents or resolved in SOURCE.parents:
        raise ValueError('Destination overlaps the source repository')
    if dest.is_symlink() or (dest.exists() and not dest.is_dir()):
        raise ValueError('Destination must be a regular directory, not a file or symlink')
    with tempfile.TemporaryDirectory(prefix='sun-ge-payload-') as tmp:
        payload = Path(tmp) / 'sun-ge'
        payload.mkdir()
        for name in PAYLOAD:
            src = SOURCE / name
            if src.is_symlink():
                raise ValueError('Refusing symbolic link: ' + str(src))
            if src.is_dir():
                snapshot(src)  # Reject nested links before copying.
                shutil.copytree(src, payload / name)
            else:
                shutil.copy2(src, payload / name)
        expected = snapshot(payload)
        current = snapshot(dest) if dest.exists() else None
        if current == expected:
            print('Already up to date: ' + str(dest))
            return
        if current is not None and not update:
            raise ValueError('Destination exists with different content. Use --update to back it up and replace it.')
        print(('Would update: ' if current is not None else 'Would install: ') + str(dest))
        if dry_run:
            print('Dry run; no destination files changed.')
            return
        dest.parent.mkdir(parents=True, exist_ok=True)
        backup = None
        if current is not None:
            backup = dest.parent / ('sun-ge-backup-' + uuid.uuid4().hex + '.zip')
            with zipfile.ZipFile(backup, 'x', zipfile.ZIP_DEFLATED) as archive:
                for path in sorted(dest.rglob('*')):
                    archive.write(path, Path('sun-ge') / path.relative_to(dest))
            print('Backup: ' + str(backup))
        # Same-filesystem staging, rollback on replacement/readback failures.
        with tempfile.TemporaryDirectory(prefix='.sun-ge-stage-', dir=dest.parent) as stage:
            stage = Path(stage)
            ready, old = stage / 'ready', stage / 'old'
            shutil.copytree(payload, ready)
            moved_old = False
            installed = False
            try:
                if dest.exists():
                    dest.rename(old)
                    moved_old = True
                ready.rename(dest)
                installed = True
                if snapshot(dest) != expected:
                    raise OSError('Installed payload failed SHA-256 verification')
            except BaseException:
                if installed:
                    shutil.rmtree(dest)
                if moved_old:
                    old.rename(dest)
                raise
        print('Verified %d files (SHA-256): %s' % (len(expected), dest))
        print('Open a new agent session and invoke sun-ge to verify discovery.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument('--agent', choices=('codex', 'claude', 'openclaw'))
    target.add_argument('--dest', help='Exact skill folder, including sun-ge (not its parent)')
    parser.add_argument('--update', action='store_true', help='Back up an existing installation to ZIP before replacing it')
    parser.add_argument('--dry-run', action='store_true', help='Validate and preview without writing the destination')
    args = parser.parse_args()
    try:
        install(destination(args), args.update, args.dry_run)
    except (OSError, ValueError) as exc:
        parser.exit(1, 'Install failed: %s\n' % exc)


if __name__ == '__main__':
    main()
