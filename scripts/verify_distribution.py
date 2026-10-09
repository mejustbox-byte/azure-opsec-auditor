"""Exercise installed wheel and sdist outside the source tree, no cloud access."""
from pathlib import Path
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


def main():
    artifacts = [ROOT/'dist/azure_opsec_auditor-0.1.0a1-py3-none-any.whl',
                 ROOT/'dist/azure_opsec_auditor-0.1.0a1.tar.gz']
    for artifact in artifacts:
        if not artifact.is_file():
            raise RuntimeError('Build wheel and sdist before verification')
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
                raise RuntimeError('Imported source instead of installed distribution')
            for name, code in [('good',0),('bad',1),('unknown',2),('not_run',2),('mixed',2)]:
                result = subprocess.run([str(cli),str(ROOT/'fixtures'/f'{name}.json'),'--as-of',AS_OF],
                                        cwd=work,capture_output=True,text=True)
                if result.returncode != code or json.loads(result.stdout)['exit_code'] != code or result.stderr:
                    raise RuntimeError('Installed CLI fixture check failed')
            result = subprocess.run([str(cli),str(ROOT/'fixtures/bad.json'),'--as-of',AS_OF,'--format','markdown'],
                                    cwd=work,capture_output=True,text=True)
            if result.returncode != 1 or 'Remediation:' not in result.stdout:
                raise RuntimeError('Installed Markdown renderer failed')
            print(f'Installed {artifact.name}: JSON/Markdown and all fixture exit codes verified outside source tree.')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
