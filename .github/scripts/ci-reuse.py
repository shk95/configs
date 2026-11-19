#!/usr/bin/env python3
"""Use proved prior PR provider checks for an equivalent master push."""
# INV repository/exact-ci-proof
import json
import os
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tool/version-control'))
from github_proof import api, reusable_provider_units

repo = os.environ['GITHUB_REPOSITORY']


def read(path, binary=False):
    return api(f'repos/{repo}/{path}', binary=binary)


try:
    reuse = reusable_provider_units(os.environ['CI_BASE'], os.environ['GITHUB_SHA'],
                                    os.environ['CI_UNITS'].split(), repo=repo, read=read)
except (subprocess.CalledProcessError, ValueError):
    print('Prior provider evidence was unavailable. The selected suites will run.')
    reuse = None
if reuse:
    print(f"Using {', '.join(reuse['units'])} from CI run {reuse['run_id']} attempt {reuse['attempt']}.")
with Path(os.environ['GITHUB_OUTPUT']).open('a') as output:
    output.write('record=' + json.dumps(reuse, separators=(',', ':')) + '\n')
    for name, unit in (('unixlike', 'unixlike:suite'), ('windows', 'windows:suite')):
        output.write(f"{name}={'true' if reuse and unit in reuse['units'] else 'false'}\n")
