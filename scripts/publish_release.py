"""Контроль выпуска через Actions: теги и существующие артефакты не перезаписываются."""
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
def asset_names(version):
    if not re.fullmatch(r'\d+\.\d+\.\d+a\d+', version, re.ASCII):
        raise ValueError('Недопустимая версия alpha-пакета')
    return (f'azure_opsec_auditor-{version}-py3-none-any.whl',
            f'azure_opsec_auditor-{version}.tar.gz', 'examples.zip', 'documentation.zip', 'SHA256SUMS')


ASSETS = asset_names('0.1.0a2')


def validate_request(tag, commit):
    if not re.fullmatch(r'v\d+\.\d+\.\d+a\d+', tag, re.ASCII):
        raise ValueError('Поддерживаются только явно указанные теги alpha-версий')
    if not re.fullmatch(r'[0-9a-f]{40}', commit, re.ASCII):
        raise ValueError('Ожидаемый commit должен быть полным SHA в нижнем регистре')


def command(args, cwd=None):
    result = subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def verify_local(source, tag, expected):
    validate_request(tag, expected)
    if command(['git', 'rev-parse', '--verify', 'HEAD^{commit}'], source) != expected:
        raise ValueError('HEAD checkout отличается от утверждённого commit выпуска')
    if command(['git', 'rev-parse', '--verify', f'refs/tags/{tag}^{{commit}}'], source) != expected:
        raise ValueError('Существующий tag отличается от утверждённого commit выпуска')
    command(['git', 'merge-base', '--is-ancestor', expected, 'origin/main'], source)
    command(['git', 'diff', '--exit-code', expected, '--'], source)
    command(['git', 'diff', '--cached', '--exit-code', expected, '--'], source)
    version = tomllib.loads((source / 'pyproject.toml').read_text())['project']['version']
    if tag != 'v' + version:
        raise ValueError('Версия пакета не соответствует тегу')
    asset_names(version)
    return version


def normalize_archives(dist, epoch, version='0.1.0a2'):
    """Нормализуются только метаданные контейнера; содержимое wheel не меняется."""
    assets = asset_names(version)
    moment = datetime.fromtimestamp(epoch, timezone.utc)
    if not 1980 <= moment.year <= 2107:
        raise ValueError('Время вне диапазона timestamps ZIP')
    wheel = dist / assets[0]
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
    sdist = dist / assets[1]
    archive = io.BytesIO()
    with tarfile.open(sdist, 'r:gz') as source, tarfile.open(fileobj=archive, mode='w', format=tarfile.PAX_FORMAT) as output:
        for member in sorted(source.getmembers(), key=lambda m: m.name):
            if not (member.isfile() or member.isdir()):
                raise ValueError('Недопустимый специальный элемент sdist')
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
                raise ValueError('Удалённый tag изменён или отличается от утверждённого commit')
            return
        if ref['type'] != 'tag' or not re.fullmatch(r'[0-9a-f]{40}', ref['sha']):
            raise ValueError('Неожиданный объект tag')
        ref = json.loads(gh('api', f'repos/{REPOSITORY}/git/tags/{ref["sha"]}'))['object']
    raise ValueError('Слишком много переходов annotated tag')


def verify_downloads(dist, downloaded, version='0.1.0a2'):
    assets = asset_names(version)
    for name in assets:
        if not (downloaded / name).is_file() or (downloaded / name).read_bytes() != (dist / name).read_bytes():
            raise ValueError('Скачанный артефакт отличается от проверенной сборки: ' + name)
    lines = (downloaded / 'SHA256SUMS').read_text().splitlines()
    if len(lines) != 4:
        raise ValueError('Неожиданный manifest контрольных сумм')
    expected_names = set(assets) - {'SHA256SUMS'}
    actual_names = set()
    for line in lines:
        digest, name = line.split('  ', 1)
        if name not in expected_names or name in actual_names:
            raise ValueError('Неожиданный/повторный элемент контрольных сумм')
        if hashlib.sha256((downloaded / name).read_bytes()).hexdigest() != digest:
            raise ValueError('Контрольная сумма опубликованного файла не совпала')
        actual_names.add(name)
    if actual_names != expected_names:
        raise ValueError('Контрольные суммы не покрывают все артефакты')


def publish(source, dist, tag, expected):
    version = verify_local(source, tag, expected)
    assets = asset_names(version)
    verify_remote_tag(tag, expected)
    release = json.loads(gh('release', 'view', tag, '--repo', REPOSITORY,
                            '--json', 'isDraft,isPrerelease,assets,targetCommitish,url'))
    if not release['isPrerelease'] or release['targetCommitish'] != expected:
        raise ValueError('Target или prerelease состояние отличаются; изменение отклонено')
    names = [a['name'] for a in release['assets']]
    if len(names) != len(set(names)) or set(names) - set(assets):
        raise ValueError('Неожиданные существующие assets; перезапись отклонена')
    # Reproducible containers let retries compare existing assets before uploading.
    if names:
        with tempfile.TemporaryDirectory(prefix='release-existing-') as temp:
            gh('release', 'download', tag, '--repo', REPOSITORY, '--dir', temp)
            for name in names:
                if (Path(temp) / name).read_bytes() != (dist / name).read_bytes():
                    raise ValueError('Существующий артефакт отличается; перезапись отклонена: ' + name)
    missing = [name for name in assets if name not in names]
    if missing and not release['isDraft']:
        raise ValueError('Опубликованный выпуск неполон; изменение отклонено')
    for name in missing:
        gh('release', 'upload', tag, str(dist / name), '--repo', REPOSITORY)
    # Download and validate ALL assets before publication, then again afterwards.
    with tempfile.TemporaryDirectory(prefix='release-before-publish-') as temp:
        gh('release', 'download', tag, '--repo', REPOSITORY, '--dir', temp)
        verify_downloads(dist, Path(temp), version)
    verify_remote_tag(tag, expected)
    if release['isDraft']:
        # Preserve the existing draft body with its exact audited CI/lab outcomes.
        gh('release', 'edit', tag, '--repo', REPOSITORY, '--draft=false', '--prerelease')
    published = json.loads(gh('release', 'view', tag, '--repo', REPOSITORY,
                              '--json', 'isDraft,isPrerelease,assets,targetCommitish,url'))
    if published['isDraft'] or not published['isPrerelease'] or published['targetCommitish'] != expected:
        raise ValueError('Проверка состояния/target публикации не пройдена')
    if {a['name'] for a in published['assets']} != set(assets) or len(published['assets']) != len(assets):
        raise ValueError('Inventory опубликованных assets не совпал')
    with tempfile.TemporaryDirectory(prefix='release-published-') as temp:
        gh('release', 'download', tag, '--repo', REPOSITORY, '--dir', temp)
        verify_downloads(dist, Path(temp), version)
    verify_remote_tag(tag, expected)
    print('Проверены опубликованный prerelease, неизменный tag, пять assets и все SHA256:', published['url'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('validate-input', 'validate-source', 'normalize', 'publish'))
    parser.add_argument('--tag', default='v0.1.0a2')
    parser.add_argument('--expected-commit', required=True)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--dist', type=Path)
    args = parser.parse_args()
    validate_request(args.tag, args.expected_commit)
    if args.operation == 'validate-input':
        return
    if args.source is None:
        parser.error('Требуется --source')
    version = verify_local(args.source, args.tag, args.expected_commit)
    if args.operation == 'validate-source':
        return
    if args.dist is None:
        parser.error('Требуется --dist')
    if args.operation == 'normalize':
        epoch = int(command(['git', 'show', '-s', '--format=%ct', args.expected_commit], args.source))
        normalize_archives(args.dist, epoch, version)
    else:
        publish(args.source, args.dist, args.tag, args.expected_commit)


if __name__ == '__main__':
    main()
