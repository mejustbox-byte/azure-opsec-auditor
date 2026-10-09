"""Exercise installed wheel and sdist outside the source tree, no cloud access."""
from pathlib import Path
from email.parser import BytesParser
import tarfile
import zipfile
import json
import os
import subprocess
import sys
import tempfile
import venv

ROOT = Path(__file__).resolve().parents[1]
AS_OF = '2026-10-09T12:00:00Z'


def run(command, cwd):
    return subprocess.run(command,cwd=cwd,check=True,capture_output=True,text=True)


def verify_license(artifact):
    """Проверяет реальные metadata и байты лицензий, не только имена файлов."""
    if artifact.suffix == '.whl':
        with zipfile.ZipFile(artifact) as archive:
            metadata_names = [n for n in archive.namelist() if n.endswith('.dist-info/METADATA')]
            if len(metadata_names) != 1:
                raise RuntimeError('Неоднозначные metadata wheel')
            metadata = BytesParser().parsebytes(archive.read(metadata_names[0]))
            prefix = metadata_names[0].removesuffix('METADATA') + 'licenses/'
            texts = {name: archive.read(prefix + name) for name in ('LICENSE', 'LICENSE.ru.md')}
    else:
        with tarfile.open(artifact, 'r:gz') as archive:
            names = archive.getnames()
            roots = {n.split('/')[0] for n in names}
            if len(roots) != 1:
                raise RuntimeError('Неоднозначный корень sdist')
            prefix = roots.pop() + '/'
            metadata = BytesParser().parsebytes(archive.extractfile(prefix + 'PKG-INFO').read())
            texts = {name: archive.extractfile(prefix + name).read() for name in ('LICENSE', 'LICENSE.ru.md')}
    if metadata['License-Expression'] != 'MIT' or set(metadata.get_all('License-File', [])) != {'LICENSE', 'LICENSE.ru.md'}:
        raise RuntimeError('MIT metadata или перечень license files не совпадают')
    for name, data in texts.items():
        if data != (ROOT / name).read_bytes():
            raise RuntimeError('Текст лицензии в пакете отличается: ' + name)
    print(f'{artifact.name}: MIT metadata и оба license files проверены.')


def main():
    artifacts = [ROOT/'dist/azure_opsec_auditor-0.1.0a2-py3-none-any.whl',
                 ROOT/'dist/azure_opsec_auditor-0.1.0a2.tar.gz']
    for artifact in artifacts:
        if not artifact.is_file():
            raise RuntimeError('Сначала соберите wheel и sdist')
        verify_license(artifact)
        with tempfile.TemporaryDirectory(prefix='opsec-install-') as temp:
            work = Path(temp)
            target = work/'venv'
            venv.EnvBuilder(with_pip=True).create(target)
            scripts = target/('Scripts' if os.name=='nt' else 'bin')
            python = scripts/('python.exe' if os.name=='nt' else 'python')
            cli = scripts/('azure-opsec-auditor.exe' if os.name=='nt' else 'azure-opsec-auditor')
            if artifact.suffix != '.whl':
                run([str(python),'-m','pip','install','--require-hashes','--only-binary=:all:',
                     '-r',str(ROOT/'requirements-build.txt')],work)
            run([str(python),'-m','pip','install','--no-index','--no-deps','--no-build-isolation',str(artifact)],work)
            run([str(python),'-m','pip','check'],work)
            location = run([str(python),'-I','-c','import azure_opsec_auditor; print(azure_opsec_auditor.__file__)'],work).stdout.strip()
            if not Path(location).is_relative_to(target):
                raise RuntimeError('Импортированы исходники вместо установленного пакета')
            for name, code in [('good',0),('bad',1),('unknown',2),('not_run',2),('mixed',2)]:
                result = subprocess.run([str(cli),str(ROOT/'fixtures'/f'{name}.json'),'--as-of',AS_OF],
                                        cwd=work,capture_output=True,text=True)
                if result.returncode != code or json.loads(result.stdout)['exit_code'] != code or result.stderr:
                    raise RuntimeError('Проверка примеров установленного CLI не пройдена')
            result = subprocess.run([str(cli),str(ROOT/'fixtures/bad.json'),'--as-of',AS_OF,'--format','markdown'],
                                    cwd=work,capture_output=True,text=True)
            if result.returncode != 1 or 'Рекомендация:' not in result.stdout:
                raise RuntimeError('Проверка установленного Markdown renderer не пройдена')
            run([str(python),'-m','pip','uninstall','--yes','azure-opsec-auditor'],work)
            run([str(python),'-I','-c',"import importlib.util; assert importlib.util.find_spec('azure_opsec_auditor') is None"],work)
            print(f'Пакет {artifact.name}: установка, JSON/Markdown, все коды примеров и удаление проверены вне исходников.')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
