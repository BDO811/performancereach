"""Install the social team into the Growth Studio worker on this Mac.

Copies the runtime and template into the worker folder, wires the social_ commands into harness.py and
seeds one workspace per product. Existing workspaces and dashboard edits are left alone.
"""
import re, shutil, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORKER = Path('/Users/amitmehta/Downloads/Serasona-Growth-Harness')
HOOK = " elif action.startswith('social_'):\n  from social_team import process_command as social_command\n  social_command(s,c)\n"


def install():
    shutil.copy2(HERE / 'runtime/social_team.py', WORKER / 'runtime/social_team.py')
    shutil.copy2(HERE / 'tests/test_social_team.py', WORKER / 'tests/test_social_team.py')
    target = WORKER / 'social-team/template'
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(HERE / 'template', target)
    h = WORKER / 'runtime/harness.py'
    text = h.read_text()
    if 'social_command' not in text:
        new, n = re.subn(r"( else:raise ValueError\('Unsupported command'\))", lambda m: HOOK + m.group(1), text, count=1)
        if not n:
            raise SystemExit('Could not find the command dispatch in harness.py')
        h.write_text(new)
    sys.path.insert(0, str(WORKER / 'runtime'))
    from harness import Store
    import social_team
    s = Store()
    for _, p, _ in s.list('growthProducts'):
        social_team.init_product(s, p['id'])
        print('Workspace ready:', p['id'])


if __name__ == '__main__':
    install()
