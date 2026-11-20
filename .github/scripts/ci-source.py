#!/usr/bin/env python3
"""Record tested identity with the workflow revision that produced it."""
# INV repository/exact-ci-proof
# INV repository/bounded-release-automation
import json
import os
from pathlib import Path
import subprocess

workflow_root = Path(__file__).resolve().parents[2]


def git(*args, cwd=None):
    return subprocess.check_output(['git', *args], cwd=cwd, text=True).strip()


payload = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
event = os.environ['GITHUB_EVENT_NAME']
pull = None
if event == 'pull_request':
    pull = payload['number']
    head = payload['pull_request']['head']['sha']
elif event == 'workflow_dispatch':
    head = payload['inputs']['head']
else:
    head = os.environ['GITHUB_SHA']
workflow_sha = git('rev-parse', 'HEAD', cwd=workflow_root)
if workflow_sha != os.environ['GITHUB_WORKFLOW_SHA']:
    raise ValueError('Evidence writer checkout differs from the actual workflow revision')
workflow_path = os.environ['GITHUB_WORKFLOW_REF'].split('/', 2)[2].split('@', 1)[0]
record = {
    'schema': 2, 'event': event, 'pull': pull, 'base': os.environ['CI_BASE'], 'head': head,
    'checkout': git('rev-parse', 'HEAD'), 'tree': git('rev-parse', 'HEAD^{tree}'),
    'workflow_sha': workflow_sha, 'workflow_blob': git('rev-parse', f'HEAD:{workflow_path}', cwd=workflow_root),
    'run_id': int(os.environ['GITHUB_RUN_ID']), 'attempt': int(os.environ['GITHUB_RUN_ATTEMPT']),
    'units': os.environ['CI_UNITS'].split(),
    'reuse': json.loads(os.environ.get('CI_REUSE') or 'null'),
}
Path(os.environ['RUNNER_TEMP'], 'source.json').write_text(json.dumps(record) + '\n')
