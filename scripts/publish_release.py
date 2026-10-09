"""Reviewed Actions release control; never creates/moves tags or overwrites assets."""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile
import tempfile
import tomllib
import zipfile

REPOSITORY = 'mejustbox-byte/azure-opsec-auditor'
ASSETS = ('azure_opsec_auditor-0.1.0a1-py3-none-any.whl',
          'azure_opsec_auditor-0.1.0a1.tar.gz', 'examples.zip', 'documentation.zip', 'SHA256SUMS')


def validate_request(tag, commit):
    if not re.fullmatch(r'v\d+\.\d+\.\d+a\d+', tag, re.ASCII):
        raise ValueError('Only explicit alpha version tags are supported')
    if not re.fullmatch(r'[0-9a-f]{40}', commit, re.ASCII):
        raise ValueError('Expected commit must be a full lowercase SHA')


def command(args, cwd=None):
    result = subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def verify_local(source, tag, expected):
    validate_request(tag, expected)
    if command(['git', 'rev-parse', '--verify', 'HEAD^{commit}'], source) != expected:
        raise ValueError('Checkout HEAD differs from approved release commit')
    if command(['git', 'rev-parse', '--verify', f'refs/tags/{tag}^{{commit}}'], source) != expected:
        raise ValueError('Existing tag differs from approved release commit')
    command(['git', 'merge-base', '--is-ancestor', expected, 'origin/main'], source)
    command(['git', 'diff', '--exit-code', expected, '--'], source)
    command(['git', 'diff', '--cached', '--exit-code', expected, '--'], source)
    version = tomllib.loads((source / 'pyproject.toml').read_text())['project']['version']
    if tag != 'v' + version or version != '0.1.0a1':
        raise ValueError('Tag/package version mismatch; this workflow releases 0.1.0a1 only')


def normalize_archives(dist, epoch):
    """Normalize container metadata only; content/checksums inside wheel are intact."""
    moment = datetime.fromtimestamp(epoch, timezone.utc)
    if not 1980 <= moment.year <= 2107:
        raise ValueError('Epoch outside ZIP timestamp range')
    wheel = dist / ASSETS[0]
    with zipfile.ZipFile(wheel) as source:
        entries = [(name, source.read(name)) for name in sorted(source.namelist())]
    with tempfile.NamedTemporaryFile(dir=dist, delete=False) as temp:
        temporary = Path(temp.name)
    try:
        with zipfile.ZipFile(temporary, 'w') as output:
            for name, data in entries:
                info = zipfile.ZipInfo(name, (moment.year, moment.month, moment.day,
                                             moment.hour, moment.minute, moment.second))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                output.writestr(info, data)
        temporary.replace(wheel)
    finally:
        temporary.unlink(missing_ok=True)
    sdist = dist / ASSETS[1]
    archive = io.BytesIO()
    with tarfile.open(sdist, 'r:gz') as source, tarfile.open(fileobj=archive, mode='w', format=tarfile.PAX_FORMAT) as output:
        for member in sorted(source.getmembers(), key=lambda m: m.name):
            if not (member.isfile() or member.isdir()):
                raise ValueError('Unsupported special member in source distribution')
            entry = tarfile.TarInfo(member.name)
            entry.type = tarfile.DIRTYPE if member.isdir() else tarfile.REGTYPE
            entry.mode = 0o755 if member.isdir() else 0o644
            entry.mtime = epoch
            entry.uid = entry.gid = 0
            entry.uname = entry.gname = ''
            data = source.extractfile(member).read() if member.isfile() else b''
            entry.size = len(data)
            output.addfile(entry, io.BytesIO(data) if data else None)
    with sdist.open('wb') as stream, gzip.GzipFile(filename='', fileobj=stream, mode='wb', mtime=epoch) as output:
        output.write(archive.getvalue())


def gh(*args):
    return command(['gh', *args])


def verify_remote_tag(tag, expected):
    ref = json.loads(gh('api', f'repos/{REPOSITORY}/git/ref/tags/{tag}'))['object']
    for _ in range(5):
        if ref['type'] == 'commit':
            if ref['sha'] != expected:
                raise ValueError('Remote tag changed or differs from approved commit')
            return
        if ref['type'] != 'tag' or not re.fullmatch(r'[0-9a-f]{40}', ref['sha']):
            raise ValueError('Unexpected tag object')
        ref = json.loads(gh('api', f'repos/{REPOSITORY}/git/tags/{ref["sha"]}'))['object']
    raise ValueError('Too many annotated tag indirections')


def verify_downloads(dist, downloaded):
    for name in ASSETS:
        if not (downloaded / name).is_file() or (downloaded / name).read_bytes() != (dist / name).read_bytes():
            raise ValueError('Downloaded release asset differs from verified build: ' + name)
    lines = (downloaded / 'SHA256SUMS').read_text().splitlines()
    if len(lines) != 4:
        raise ValueError('Unexpected checksum manifest')
    expected_names = set(ASSETS) - {'SHA256SUMS'}
    actual_names = set()
    for line in lines:
        digest, name = line.split('  ', 1)
        if name not in expected_names or name in actual_names:
            raise ValueError('Unexpected/duplicate checksum member')
        if hashlib.sha256((downloaded / name).read_bytes()).hexdigest() != digest:
            raise ValueError('Published checksum mismatch')
        actual_names.add(name)
    if actual_names != expected_names:
        raise ValueError('Incomplete checksum coverage')


def publish(source, dist, tag, expected):
    verify_local(source, tag, expected)
    verify_remote_tag(tag, expected)
    release = json.loads(gh('release', 'view', tag, '--repo', REPOSITORY,
                            '--json', 'isDraft,isPrerelease,assets,targetCommitish,url'))
    if not release['isPrerelease'] or release['targetCommitish'] != expected:
        raise ValueError('Existing release target or prerelease state differs; refusing modification')
    names = [a['name'] for a in release['assets']]
    if len(names) != len(set(names)) or set(names) - set(ASSETS):
        raise ValueError('Unexpected existing release assets; no assets will be overwritten')
    # Reproducible containers let retries compare existing assets before uploading.
    if names:
        with tempfile.TemporaryDirectory(prefix='release-existing-') as temp:
            gh('release', 'download', tag, '--repo', REPOSITORY, '--dir', temp)
            for name in names:
                if (Path(temp) / name).read_bytes() != (dist / name).read_bytes():
                    raise ValueError('Existing asset differs; refusing overwrite: ' + name)
    missing = [name for name in ASSETS if name not in names]
    if missing and not release['isDraft']:
        raise ValueError('Published release has incomplete assets; refusing modification')
    for name in missing:
        gh('release', 'upload', tag, str(dist / name), '--repo', REPOSITORY)
    # Download and validate ALL assets before publication, then again afterwards.
    with tempfile.TemporaryDirectory(prefix='release-before-publish-') as temp:
        gh('release', 'download', tag, '--repo', REPOSITORY, '--dir', temp)
        verify_downloads(dist, Path(temp))
    verify_remote_tag(tag, expected)
    if release['isDraft']:
        # Preserve the existing draft body with its exact audited CI/lab outcomes.
        gh('release', 'edit', tag, '--repo', REPOSITORY, '--draft=false', '--prerelease')
    published = json.loads(gh('release', 'view', tag, '--repo', REPOSITORY,
                              '--json', 'isDraft,isPrerelease,assets,targetCommitish,url'))
    if published['isDraft'] or not published['isPrerelease'] or published['targetCommitish'] != expected:
        raise ValueError('Publication state/target verification failed')
    if {a['name'] for a in published['assets']} != set(ASSETS) or len(published['assets']) != len(ASSETS):
        raise ValueError('Published asset inventory mismatch')
    with tempfile.TemporaryDirectory(prefix='release-published-') as temp:
        gh('release', 'download', tag, '--repo', REPOSITORY, '--dir', temp)
        verify_downloads(dist, Path(temp))
    verify_remote_tag(tag, expected)
    print('Verified published prerelease, immutable tag, five assets and all SHA256:', published['url'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('validate-input', 'validate-source', 'normalize', 'publish'))
    parser.add_argument('--tag', default='v0.1.0a1')
    parser.add_argument('--expected-commit', required=True)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--dist', type=Path)
    args = parser.parse_args()
    validate_request(args.tag, args.expected_commit)
    if args.operation == 'validate-input':
        return
    if args.source is None:
        parser.error('--source is required')
    verify_local(args.source, args.tag, args.expected_commit)
    if args.operation == 'validate-source':
        return
    if args.dist is None:
        parser.error('--dist is required')
    if args.operation == 'normalize':
        epoch = int(command(['git', 'show', '-s', '--format=%ct', args.expected_commit], args.source))
        normalize_archives(args.dist, epoch)
    else:
        publish(args.source, args.dist, args.tag, args.expected_commit)


if __name__ == '__main__':
    main()
