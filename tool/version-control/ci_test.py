"""Simulated Actions transport for real Git source identities."""
# INV repository/exact-ci-proof
import io
import json
import zipfile

import github_proof as proof
from repo_policy import load


def archive(value):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w') as zipped:
        zipped.writestr('source.json', json.dumps(value))
    return stream.getvalue()


class Evidence:
    def __init__(self, git, base, head, tree, units, *, run_id=7, pull=None, event='workflow_dispatch'):
        policy = load()
        self.id = run_id
        self.path = f'actions/runs/{run_id}'
        repo = 'fixture/configs'
        commit = head
        run_head = base if event == 'workflow_dispatch' else head
        workflow = base if event == 'workflow_dispatch' else head
        if event == 'pull_request':
            commit = git('commit-tree', tree, '-p', base, '-p', head, '-m', 'Merge CI fixture')
            workflow = commit
        self.run = dict(id=run_id, repository={'full_name': repo}, head_repository={'full_name': repo},
                        path=policy['ci']['workflow'], head_branch=policy['base_branch'], head_sha=run_head,
                        run_attempt=1, status='completed', conclusion='success', event=event,
                        html_url=f'https://github.com/{repo}/{self.path}')
        self.source = dict(schema=2, event=event, base=base, head=head, tree=tree, checkout=commit,
                           pull=pull, run_id=run_id, attempt=1, units=units, reuse=None, workflow_sha=workflow,
                           workflow_blob=git('rev-parse', f"{workflow}:{policy['ci']['workflow']}"))
        self.commit = {'sha': commit, 'tree': {'sha': tree}, 'parents': [{'sha': p} for p in (base, head)]}
        self.artifacts = [dict(id=run_id, name='ci-source-1', expired=False, workflow_run={'id': run_id})]
        self.jobs = {}
        self.set_job('Classify change', 'ubuntu-latest', 'Resolve owning scopes and CI effects')
        if event == 'push':
            self.set_job('Classify change', 'ubuntu-latest', 'Resolve owning scopes and CI effects',
                         'Resolve previous provider evidence')
        self.set_job(proof.POLICY_JOB, 'ubuntu-latest', *proof.POLICY_STEPS)
        self.set_job(policy['ci']['gate'], 'ubuntu-latest', 'Enforce scoped results', 'Record the tested source')
        self.set_job(proof.TOPIC_JOB, 'ubuntu-latest', *proof.TOPIC_STEPS, selected=event == 'pull_request')
        for name, runner, _ in proof.UNITS.values():
            self.set_job(name, runner, selected=False)
        for unit in units:
            name, runner, steps = proof.UNITS[unit]
            prior = [step['name'] for step in self.jobs[name]['steps']]
            self.set_job(name, runner, *dict.fromkeys([*prior, *steps]))

    def set_job(self, name, runner, *steps, selected=True):
        self.jobs[name] = dict(name=name, labels=[runner], run_id=self.id, run_attempt=1,
                               head_sha=self.run['head_sha'], conclusion='success' if selected else 'skipped',
                               steps=[dict(name=step, conclusion='success') for step in steps] if selected else [])

    def read(self, path, binary=False):
        if path == self.path:
            return self.run
        if path == f'{self.path}/attempts/{self.run["run_attempt"]}/jobs?per_page=100':
            return {'total_count': len(self.jobs), 'jobs': list(self.jobs.values())}
        if path == f'{self.path}/artifacts?per_page=100':
            return {'total_count': len(self.artifacts), 'artifacts': self.artifacts}
        if path == f'actions/artifacts/{self.id}/zip' and binary:
            return archive(self.source)
        if path == f'git/commits/{self.commit["sha"]}':
            return self.commit
        raise AssertionError('Unexpected CI read: ' + path)
