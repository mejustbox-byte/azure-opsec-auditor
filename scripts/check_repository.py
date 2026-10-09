"""Best-effort credential signature scan and local documentation link check."""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
# Only signatures; do not print matched values. This is not a proof of secrecy.
SIGNATURES = (
    re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    re.compile(rb'gh[pousr]_[A-Za-z0-9]{20,}'),
    re.compile(rb'github_pat_[A-Za-z0-9_]{30,}'),
    re.compile(rb'AKIA[0-9A-Z]{16}'),
    re.compile(rb'(?i)(?:client_secret|password|access_token)\s*[=:]\s*[\"\x27][^\"\x27\r\n]{12,}'),
)


def scan_bytes(data):
    return any(pattern.search(data) for pattern in SIGNATURES)


def main():
    result = subprocess.run(['git','ls-files','-z','--cached','--others','--exclude-standard'],
                            cwd=ROOT,check=True,capture_output=True)
    paths = sorted(set(result.stdout.decode('utf-8').split('\0')) - {''})
    failures = 0
    for relative in paths:
        path = ROOT / relative
        if not path.is_file():
            continue
        data = path.read_bytes()
        if scan_bytes(data):
            print('Возможная сигнатура credentials в файле (значение скрыто):',relative)
            failures += 1
        if path.suffix == '.md':
            for link in re.findall(r'\]\(([^)]+)\)',data.decode('utf-8')):
                if '://' in link or link.startswith('#'):
                    continue
                target = path.parent / link.split('#')[0]
                if not target.is_file():
                    print('Неработающая локальная ссылка в:',relative)
                    failures += 1

    index = (ROOT / 'README.md').read_text()
    indexed = set(re.findall(r'\]\(([^)#]+)(?:#[^)]*)?\)', index))
    documents = [*ROOT.glob('*.md'), *ROOT.glob('docs/**/*.md'), *ROOT.glob('.github/**/*.md')]
    for document in documents:
        relative = document.relative_to(ROOT).as_posix()
        if relative != 'README.md' and relative not in indexed:
            print('Документ отсутствует в полном README index:', relative)
            failures += 1
    print(f'Проверено {len(paths)} файлов; ошибок сигнатур/ссылок/индекса: {failures}.')
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
