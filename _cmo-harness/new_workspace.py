"""Create a CMO harness workspace for one brand: PerformanceReach itself, or one client.

    python3 -I _cmo-harness/new_workspace.py <folder>

The folder must not exist yet. Real brand data lives in the workspace, never in this public repo.
"""
import shutil
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent / 'template'


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    dest = Path(sys.argv[1]).expanduser().resolve()
    if dest.exists():
        sys.exit(f'{dest} already exists. Pick a new folder so no workspace is overwritten.')
    if not (TEMPLATE / 'CLAUDE.md').exists():
        sys.exit('template/ is missing. Run python3 -I _cmo-harness/build.py first.')
    shutil.copytree(TEMPLATE, dest, ignore=shutil.ignore_patterns('.gitkeep'))
    print(f'Workspace ready: {dest}')
    print('Next: fill the six files in owner/, then run `claude` in that folder and type /run-week.')


if __name__ == '__main__':
    main()
