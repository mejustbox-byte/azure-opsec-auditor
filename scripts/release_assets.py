"""Create only synthetic/documentation release assets; inspect all archive text."""
from pathlib import Path
import hashlib
import tarfile
import zipfile
from check_repository import scan_bytes

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT/'dist'


def archive(name, files):
    with zipfile.ZipFile(DIST/name,'w',compression=zipfile.ZIP_DEFLATED) as output:
        for path in sorted(files):
            data = path.read_bytes()
            if scan_bytes(data):
                raise RuntimeError('Credential signature in release input; value withheld')
            info = zipfile.ZipInfo(path.relative_to(ROOT).as_posix(), date_time=(1980,1,1,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            output.writestr(info,data)


def inspect(path):
    if path.suffix in ('.whl','.zip'):
        with zipfile.ZipFile(path) as source:
            payloads = [source.read(n) for n in source.namelist() if not n.endswith('/')]
    else:
        with tarfile.open(path,'r:gz') as source:
            payloads = [source.extractfile(m).read() for m in source.getmembers() if m.isfile()]
    if any(scan_bytes(data) for data in payloads):
        raise RuntimeError('Credential signature in release archive; value withheld')


def main():
    DIST.mkdir(exist_ok=True)
    archive('examples.zip', [*ROOT.glob('fixtures/*.json'),*ROOT.glob('schemas/*.json')])
    archive('documentation.zip', [ROOT/'README.md',ROOT/'SECURITY.md',*ROOT.glob('docs/*.md'),*ROOT.glob('schemas/*.json')])
    names = ['azure_opsec_auditor-0.1.0a1-py3-none-any.whl',
             'azure_opsec_auditor-0.1.0a1.tar.gz','documentation.zip','examples.zip']
    lines=[]
    for name in names:
        path = DIST/name
        inspect(path)
        lines.append(f'{hashlib.sha256(path.read_bytes()).hexdigest()}  {name}')
    (DIST/'SHA256SUMS').write_text('\n'.join(lines)+'\n')
    print('Verified archive signatures; wrote four assets and SHA256SUMS.')


if __name__=='__main__':
    main()
