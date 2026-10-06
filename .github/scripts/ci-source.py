#!/usr/bin/env python3
"""Record tested source identities; execution status remains in GitHub Actions."""
import json
import os
from pathlib import Path
import subprocess

# INV repository/bounded-release-automation
payload = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
event = os.environ['GITHUB_EVENT_NAME']
head = payload['pull_request']['head']['sha'] if event == 'pull_request' else os.environ['GITHUB_SHA']
record = {'event': event, 'base': os.environ['CI_BASE'], 'head': head,
          'tree': subprocess.check_output(['git', 'rev-parse', 'HEAD^{tree}'], text=True).strip()}
Path(os.environ['RUNNER_TEMP'], 'source.json').write_text(json.dumps(record) + '\n')
