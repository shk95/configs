#!/usr/bin/env python3
"""Local consumer development; state belongs to this checkout's Git directory.

INV unixlike/local-consumer-development
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys

sys.dont_write_bytecode = True


class Refused(RuntimeError):
    pass


def run(argv, cwd=None, capture=True, env=None):
    result = subprocess.run([str(v) for v in argv], cwd=cwd, env=env, text=True,
                            stdout=subprocess.PIPE if capture else None, check=True)
    return result.stdout.strip() if capture else None


def git(root, *args):
    return run(['git', '-C', root, *args], env=dict(os.environ, GIT_OPTIONAL_LOCKS='0'))


def read_json(path):
    return json.loads(path.read_text())


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = path.with_suffix('.tmp')
    with temporary.open('w') as stream:
        os.chmod(temporary, 0o600)
        json.dump(value, stream, indent=2)
        stream.write('\n')
    temporary.replace(path)


def inventory(root, subdir=''):
    """Only Git-visible source: no notes, ignored credentials, or local state."""
    output = subprocess.check_output(['git', '-C', str(root), 'ls-files', '-z',
                                      '--cached', '--others', '--exclude-standard', '--', subdir or '.'])
    files = {}
    for raw in sorted(set(output.split(b'\0')) - {b''}):
        relative = os.fsdecode(raw)
        if 'notes' in Path(relative).parts:
            continue
        path = root / relative
        if not path.exists() and not path.is_symlink():
            continue
        if path.is_symlink():
            raise Refused(f'Source symlinks need an explicit tracked copy before development: {path}')
        if not path.is_file():
            raise Refused(f'Unsupported source entry (including submodules): {path}')
        key = str(Path(relative).relative_to(subdir)) if subdir else relative
        files[key] = (path.read_bytes(), bool(path.stat().st_mode & stat.S_IXUSR))
    return files


def digest(files):
    value = hashlib.sha256()
    for name, (content, executable) in sorted(files.items()):
        value.update(json.dumps([name, executable, len(content)]).encode() + b'\0' + content)
    return value.hexdigest()


def snapshot(root, parent, subdir=''):
    files = inventory(root, subdir)
    identity = digest(files)
    destination = parent / identity
    if not destination.exists():
        destination.mkdir(parents=True, mode=0o700)
        for name, (content, executable) in files.items():
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
            target.chmod(0o755 if executable else 0o644)
    # Check cached snapshots too: interrupted writes or local edits must not be reused.
    if any(p.is_symlink() for p in destination.rglob('*')):
        raise Refused(f'Snapshot contains a symlink: {destination}')
    actual = {str(p.relative_to(destination)): (p.read_bytes(), bool(p.stat().st_mode & stat.S_IXUSR))
              for p in destination.rglob('*') if p.is_file()}
    if digest(actual) != identity:
        raise Refused(f'Snapshot has changed or is incomplete: {destination}')
    return identity, destination


def validate_recipe(value):
    if set(value) != {'version', 'release', 'provider_publish', 'consumer_publish', 'verify'} or value['version'] != 1:
        raise Refused('Recipe requires version=1, release, provider_publish, consumer_publish, verify.')
    if not re.fullmatch(r'unixlike-v(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)', value['release']):
        raise Refused('Recipe release must be an exact Unix-like SemVer tag.')
    for key in ('provider_publish', 'consumer_publish', 'verify'):
        command = value[key]
        if not isinstance(command, list) or not all(isinstance(v, str) and v for v in command):
            raise Refused(f'{key} must be an argv array; shell strings are not accepted.')
        if key != 'verify' and not command:
            raise Refused(f'{key} needs an explicit command implementing the repository procedure.')
    return value


class Development:
    def __init__(self, root):
        self.root = root
        self.local = Path(git(root, 'rev-parse', '--absolute-git-dir')) / 'configs-dev'
        self.connection_file = self.local / 'connection.json'
        self.session_file = self.local / 'session.json'
        self.promotion_file = self.local / 'promotion.json'

    @contextmanager
    def operation_lock(self, read_only=False):
        if read_only:
            try:
                lock = (self.local / 'lock').open('r')
            except FileNotFoundError:
                if any((self.local / name).exists() for name in
                       ('connection.json', 'session.json', 'promotion.json', 'recipe.json')):
                    raise Refused('Local development records have no coordination lock; preserve and inspect them before reconnecting.')
                # No records are read without a lock. A later writer may
                # initialize state; this result names the observed absence.
                yield False
                return
        else:
            self.local.mkdir(mode=0o700, exist_ok=True)
            lock = (self.local / 'lock').open('a')
        with lock:
            try:
                fcntl.flock(lock, (fcntl.LOCK_SH if read_only else fcntl.LOCK_EX) | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise Refused('Another development operation is running in this checkout.') from error
            yield True

    def info(self):
        with self.operation_lock(read_only=True) as coordinated:
            connection = consumer = None
            if coordinated and self.connection_file.exists():
                connection, consumer = self.connection()
            return {
                'schema': 1, 'state': 'connected' if consumer else 'disconnected' if coordinated else 'uninitialized',
                'coordination': 'shared-lock' if coordinated else 'no-records-observed',
                'connection': connection, 'local_state': str(self.local),
                'provider_head': git(self.root, 'rev-parse', 'HEAD'),
                'provider_branch': git(self.root, 'branch', '--show-current'),
                'provider_status': git(self.root, 'status', '--short'),
                'consumer_head': git(consumer, 'rev-parse', 'HEAD') if consumer else None,
                'consumer_branch': git(consumer, 'branch', '--show-current') if consumer else None,
                'consumer_status': git(consumer, 'status', '--short') if consumer else None,
                'session': read_json(self.session_file) if coordinated and self.session_file.exists() else None,
                'promotion': read_json(self.promotion_file) if coordinated and self.promotion_file.exists() else None,
            }

    def connection(self):
        if not self.connection_file.exists():
            raise Refused('No local consumer connection. Run just dev-connect <checkout> <host>.')
        value = read_json(self.connection_file)
        if (not isinstance(value, dict) or set(value) != {'version', 'consumer', 'host'} or
                type(value['version']) is not int or value['version'] != 1 or
                not isinstance(value['consumer'], str) or not Path(value['consumer']).is_absolute() or
                not isinstance(value['host'], str) or not re.fullmatch(r'[A-Za-z0-9_-]+', value['host'])):
            raise Refused('Invalid local consumer connection: expected version 1, an absolute consumer path and a host identifier.')
        consumer = Path(value['consumer'])
        if not consumer.is_dir() or git(consumer, 'rev-parse', '--show-toplevel') != str(consumer):
            raise Refused('The selected consumer checkout is missing or has moved; reconnect explicitly.')
        return value, consumer

    def adapter(self, consumer, *args, capture=True):
        entry = consumer / 'tool/configs-dev'
        if not entry.is_file():
            raise Refused('Consumer must provide its own executable tool/configs-dev adapter (protocol 1).')
        return run([entry, *args], cwd=consumer, capture=capture)

    def guard_promotion(self):
        if self.promotion_file.exists():
            plan = read_json(self.promotion_file)
            if plan['completed'] and plan['completed'] != plan['steps']:
                raise Refused('An incomplete promotion is preserved; resume it before replacing this connection or application.')

    def connect(self, path, host):
        self.guard_promotion()
        consumer = Path(path).expanduser().resolve()
        if consumer == self.root or consumer in self.root.parents or self.root in consumer.parents:
            raise Refused('Select a separate consumer Git checkout.')
        if git(consumer, 'rev-parse', '--show-toplevel') != str(consumer):
            raise Refused('Connection must name the consumer checkout root.')
        if self.adapter(consumer, 'protocol') != '1':
            raise Refused('Unsupported consumer development protocol.')
        value = {'version': 1, 'consumer': str(consumer), 'host': host}
        if not re.fullmatch(r'[A-Za-z0-9_-]+', host):
            raise Refused('Invalid host selection.')
        # Resolve against local provider before saving; failed connections preserve existing state.
        _, provider = snapshot(self.root, self.local / 'sources/provider', 'unixlike')
        _, source = snapshot(consumer, self.local / 'sources/consumer')
        self.adapter(consumer, 'resolve', host, '--flake', f'path:{source}', '--provider', f'path:{provider}')
        write_json(self.connection_file, value)
        self.session_file.unlink(missing_ok=True)
        self.promotion_file.unlink(missing_ok=True)
        print(f'Connected locally: {consumer} ({host})')

    def recipe(self):
        path = self.local / 'recipe.json'
        if not path.exists():
            raise Refused('Configure a local promotion recipe first: just dev-configure <recipe.json>.')
        return validate_recipe(read_json(path))

    def pair(self, pinned=False, host=None):
        connection, consumer = self.connection()
        selected = host or connection['host']
        provider_id, provider = snapshot(self.root, self.local / 'sources/provider', 'unixlike')
        consumer_id, source = snapshot(consumer, self.local / 'sources/consumer')
        args = ['--flake', f'path:{source}']
        if not pinned:
            args += ['--provider', f'path:{provider}']
        selector = json.loads(self.adapter(consumer, 'resolve', selected, *args))
        if set(selector) != {'constructor', 'output'} or selector['constructor'] not in ('mkNixos', 'mkDarwin', 'mkHome'):
            raise Refused('Invalid consumer output selector.')
        return {'host': selected, 'consumer': str(consumer), 'provider_id': provider_id,
                'consumer_id': consumer_id, 'provider_source': str(provider),
                'consumer_source': str(source), 'pinned': pinned, 'selector': selector}

    @staticmethod
    def nix_args(pair):
        args = ['--no-write-lock-file']
        if not pair['pinned']:
            args += ['--override-input', 'configs', f"path:{pair['provider_source']}"]
        return args

    def evaluate(self, pair):
        output = f"path:{pair['consumer_source']}#{pair['selector']['output']}"
        drv = run(['nix', 'eval', '--raw', *self.nix_args(pair), output + '.drvPath'])
        print(json.dumps({'host': pair['host'], 'pinned': pair['pinned'], 'derivation': drv}))
        return drv

    def build(self, pair):
        output = f"path:{pair['consumer_source']}#{pair['selector']['output']}"
        paths = json.loads(run(['nix', 'build', '--json', '--no-link', *self.nix_args(pair), output]))
        if len(paths) != 1 or set(paths[0]['outputs']) != {'out'}:
            raise Refused('Expected exactly one host closure output.')
        package = paths[0]['outputs']['out']
        print(json.dumps({'host': pair['host'], 'pinned': pair['pinned'], 'package': package}))
        return package

    def unchanged(self, pair, consumer=True):
        for kind in ('provider', 'consumer'):
            path = Path(pair[f'{kind}_source'])
            if any(p.is_symlink() for p in path.rglob('*')):
                raise Refused(f'{kind} snapshot contains a symlink.')
            files = {str(p.relative_to(path)): (p.read_bytes(), bool(p.stat().st_mode & stat.S_IXUSR))
                     for p in path.rglob('*') if p.is_file()}
            if digest(files) != pair[f'{kind}_id']:
                raise Refused(f'{kind} snapshot was changed; inspect the local evidence.')
        if digest(inventory(self.root, 'unixlike')) != pair['provider_id']:
            raise Refused('Provider source changed; apply and verify the new source pair.')
        if consumer and digest(inventory(Path(pair['consumer']))) != pair['consumer_id']:
            raise Refused('Consumer source changed; apply and verify the new source pair.')

    def session(self):
        if not self.session_file.exists():
            raise Refused('No successful development application. Run just dev-apply first.')
        value = read_json(self.session_file)
        connection, _ = self.connection()
        if value['consumer'] != connection['consumer'] or value['host'] != connection['host']:
            raise Refused('The applied session does not match the current connection.')
        self.unchanged(value)
        return value

    def apply(self):
        self.guard_promotion()
        pair = self.pair()
        package = self.build(pair)
        self.unchanged(pair)
        # Invalidate previous verification BEFORE a possibly partial activation.
        self.session_file.unlink(missing_ok=True)
        self.promotion_file.unlink(missing_ok=True)
        self.adapter(Path(pair['consumer']), 'apply', pair['host'],
                     '--flake', f"path:{pair['consumer_source']}",
                     '--provider', f"path:{pair['provider_source']}", '--package', package, capture=False)
        self.unchanged(pair)
        pair.update(package=package, verified=False)
        write_json(self.session_file, pair)

    def environment(self, pair, recipe=None):
        env = os.environ.copy()
        for key, value in {'PROVIDER': str(self.root), 'CONSUMER': pair['consumer'],
                           'HOST': pair['host'], 'PACKAGE': pair['package'],
                           'PROVIDER_SOURCE': pair['provider_source'],
                           'CONSUMER_SOURCE': pair['consumer_source'],
                           'RELEASE': recipe['release'] if recipe else ''}.items():
            env[f'CONFIGS_DEV_{key}'] = value
        return env

    def verify(self, note):
        pair = self.session()
        pair['verified'] = False
        write_json(self.session_file, pair)
        source_args = ['--flake', f"path:{pair['consumer_source']}"]
        if not pair['pinned']:
            source_args += ['--provider', f"path:{pair['provider_source']}"]
        self.adapter(Path(pair['consumer']), 'verify', pair['host'],
                     *source_args, '--package', pair['package'], capture=False)
        recipe_path = self.local / 'recipe.json'
        recipe = None
        if recipe_path.exists():
            recipe = self.recipe()
            if recipe['verify']:
                run(recipe['verify'], cwd=pair['consumer'], env=self.environment(pair, recipe), capture=False)
        if not note or not note.strip():
            raise Refused('Supply --note with the functional runtime checks you actually completed.')
        self.unchanged(pair)
        pair.update(verified=True, runtime_note=note, verification_recipe=recipe)
        write_json(self.session_file, pair)
        print('Applied package and recorded runtime checks verified; no release was created.')

    def release_source(self, pair, recipe):
        tag = recipe['release']
        if git(self.root, 'cat-file', '-t', f'refs/tags/{tag}') != 'tag':
            raise Refused('The selected release must be annotated.')
        source = git(self.root, 'rev-parse', f'refs/tags/{tag}^{{commit}}')
        git(self.root, 'merge-base', '--is-ancestor', source, 'master')
        # Compare source CONTENT to what was actually tested, including new files and modes.
        entries = subprocess.check_output(['git', '-C', str(self.root), 'ls-tree', '-rz', source, '--', 'unixlike'])
        files = {}
        for entry in entries.split(b'\0'):
            if not entry:
                continue
            header, name = entry.split(b'\t', 1)
            mode, kind, blob = header.split()
            if kind != b'blob' or mode not in (b'100644', b'100755'):
                raise Refused('Release source contains unsupported entries.')
            key = str(Path(os.fsdecode(name)).relative_to('unixlike'))
            files[key] = (subprocess.check_output(['git', '-C', str(self.root), 'cat-file', 'blob', blob.decode()]), mode == b'100755')
        if digest(files) != pair['provider_id']:
            raise Refused('Published provider content differs from the tested provider.')
        run([self.root / 'tool/configs', 'audit', '--tag', tag], cwd=self.root, capture=False)
        remote = git(self.root, 'ls-remote', 'origin', f'refs/tags/{tag}^{{}}')
        if remote.split() != [source, f'refs/tags/{tag}^{{}}']:
            raise Refused('Exact annotated release has not been published to origin.')
        return source

    def promote(self, execute=False):
        recipe = self.recipe()
        if not execute:
            if self.promotion_file.exists():
                previous = read_json(self.promotion_file)
                if previous['completed'] and previous['completed'] != previous['steps']:
                    print(json.dumps(previous, indent=2))
                    return
            pair = self.session()
            if not pair['verified'] or pair.get('verification_recipe') != recipe:
                raise Refused('Run dev-verify with completed runtime checks and the current recipe before promotion.')
            declaration = read_json(Path(pair['provider_source']) / 'release.json')
            if recipe['release'] != 'unixlike-v' + declaration['version']:
                raise Refused('Recipe release differs from the tested source-owned release declaration.')
            plan = {'version': 1, 'pair': pair, 'recipe': recipe, 'completed': [],
                    'steps': ['provider-check', 'provider-publish', 'consumer-adopt',
                              'pinned-build', 'consumer-publish', 'pinned-apply', 'pinned-verify']}
            write_json(self.promotion_file, plan)
            print(json.dumps(plan, indent=2))
            return
        if not self.promotion_file.exists():
            raise Refused('Review just dev-promote --plan before executing.')
        plan = read_json(self.promotion_file)
        pair = plan['pair']
        if recipe != plan['recipe']:
            raise Refused('Promotion recipe changed; review a new plan.')
        connection, consumer = self.connection()
        if connection['consumer'] != pair['consumer'] or connection['host'] != pair['host']:
            raise Refused('Promotion connection changed.')
        self.unchanged(pair, consumer=False)
        if 'release_source' in plan:
            if self.release_source(pair, recipe) != plan['release_source']:
                raise Refused('Published release identity changed since the saved checkpoint.')
        if 'pinned' in plan:
            self.unchanged(plan['pinned'])
        expected = plan.get('consumer_after_adopt', pair['consumer_id'])
        if digest(inventory(consumer)) != expected:
            raise Refused('Consumer changed outside the planned adoption; inspect and re-test.')
        env = self.environment(pair, recipe)
        self.adapter(consumer, 'verify', pair['host'], '--flake',
                     f"path:{pair['consumer_source']}", '--provider',
                     f"path:{pair['provider_source']}", '--package', pair['package'], capture=False)
        for step in plan['steps']:
            if step in plan['completed']:
                continue
            print(f'Promotion: {step}', flush=True)
            if 'pinned' in plan:
                self.unchanged(plan['pinned'])
            if step == 'provider-check':
                run(['just', 'check'], cwd=self.root, capture=False)
            elif step == 'provider-publish':
                run(recipe['provider_publish'], cwd=self.root, env=env, capture=False)
                plan['release_source'] = self.release_source(pair, recipe)
            elif step == 'consumer-adopt':
                self.release_source(pair, recipe)
                before = inventory(consumer)
                try:
                    self.adapter(consumer, 'adopt', '--release', recipe['release'],
                                 '--source', plan['release_source'], capture=False)
                finally:
                    after = inventory(consumer)
                    stable = lambda files: {k: v for k, v in files.items() if k not in ('flake.nix', 'flake.lock')}
                    if stable(before) != stable(after):
                        raise Refused('Adoption changed files outside flake.nix and flake.lock; inspect before retrying.')
                    plan['consumer_after_adopt'] = digest(after)
                    write_json(self.promotion_file, plan)
            elif step == 'pinned-build':
                pinned = self.pair(pinned=True)
                self.evaluate(pinned)
                package = self.build(pinned)
                if package != pair['package']:
                    raise Refused('Pinned closure differs from the tested closure; preserve changes and re-test explicitly.')
                plan['pinned'] = pinned
            elif step == 'consumer-publish':
                run(recipe['consumer_publish'], cwd=consumer, env=env, capture=False)
                if git(consumer, 'status', '--porcelain'):
                    raise Refused('Consumer publication left uncommitted changes.')
                head = git(consumer, 'rev-parse', 'HEAD')
                git(consumer, 'merge-base', '--is-ancestor', head, 'master')
                remote = git(consumer, 'ls-remote', 'origin', 'refs/heads/master')
                if remote.split() != [head, 'refs/heads/master']:
                    raise Refused('Consumer HEAD must be the published master after the publication procedure.')
            elif step == 'pinned-apply':
                pinned = plan['pinned']
                self.adapter(consumer, 'apply', pair['host'], '--flake',
                             f"path:{pinned['consumer_source']}", '--package', pair['package'], capture=False)
            elif step == 'pinned-verify':
                self.adapter(consumer, 'verify', pair['host'], '--flake',
                             f"path:{plan['pinned']['consumer_source']}", '--package', pair['package'], capture=False)
                if recipe['verify']:
                    run(recipe['verify'], cwd=consumer, env=env, capture=False)
            self.unchanged(pair, consumer=False)
            expected = plan.get('consumer_after_adopt', pair['consumer_id'])
            if digest(inventory(consumer)) != expected:
                raise Refused(f'{step} changed consumer content beyond the explicit adoption.')
            plan['completed'].append(step)
            write_json(self.promotion_file, plan)
        final = dict(plan['pinned'])
        final.update(package=pair['package'], verified=True, runtime_note=pair['runtime_note'],
                     verification_recipe=recipe, promoted_release=recipe['release'])
        write_json(self.session_file, final)
        print('Promotion completed: exact release adopted, published, applied and verified.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='operation', required=True)
    connect = sub.add_parser('connect')
    connect.add_argument('consumer')
    connect.add_argument('host')
    sub.add_parser('disconnect')
    sub.add_parser('info')
    configure = sub.add_parser('configure')
    configure.add_argument('recipe', type=Path)
    for action in ('eval', 'build'):
        command = sub.add_parser(action)
        command.add_argument('host', nargs='?')
        command.add_argument('--pinned', action='store_true')
    sub.add_parser('apply')
    verify = sub.add_parser('verify')
    verify.add_argument('--note', required=True)
    promotion = sub.add_parser('promote')
    mode = promotion.add_mutually_exclusive_group(required=True)
    mode.add_argument('--plan', action='store_true')
    mode.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    development = Development(root)
    if args.operation == 'info':
        print(json.dumps(development.info(), indent=2))
        return
    # One operation per checkout: concurrent activation/promotion must not share receipts.
    with development.operation_lock():
        if args.operation == 'connect':
            development.connect(args.consumer, args.host)
        elif args.operation == 'disconnect':
            development.guard_promotion()
            development.connection_file.unlink(missing_ok=True)
            development.session_file.unlink(missing_ok=True)
            development.promotion_file.unlink(missing_ok=True)
            print('Disconnected. Source snapshots and recipe are preserved in the local Git directory.')
        elif args.operation == 'configure':
            recipe_path = args.recipe.expanduser().resolve()
            if recipe_path.is_relative_to(root):
                ignored = subprocess.run(['git', '-C', str(root), 'check-ignore', '-q', '--',
                                          str(recipe_path.relative_to(root))]).returncode == 0
                if not ignored:
                    raise Refused('Keep the private recipe outside provider source or in a Git-ignored local file.')
            if development.promotion_file.exists():
                previous = read_json(development.promotion_file)
                if previous['completed'] and previous['completed'] != previous['steps']:
                    raise Refused('Finish or inspect the in-progress promotion before changing its recipe.')
            write_json(development.local / 'recipe.json', validate_recipe(read_json(recipe_path)))
            if development.session_file.exists():
                session = read_json(development.session_file)
                session['verified'] = False
                write_json(development.session_file, session)
            development.promotion_file.unlink(missing_ok=True)
            print('Local recipe saved. Publication commands run only with dev-promote --execute.')
        elif args.operation in ('eval', 'build'):
            pair = development.pair(args.pinned, args.host)
            getattr(development, 'evaluate' if args.operation == 'eval' else 'build')(pair)
        elif args.operation == 'apply':
            development.apply()
        elif args.operation == 'verify':
            development.verify(args.note)
        else:
            development.promote(args.execute)


if __name__ == '__main__':
    try:
        main()
    except (Refused, OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(f'configs development: {error}', file=sys.stderr)
        sys.exit(1)
