"""Release control invariants; no real token, API call or upload in unit tests."""
from contextlib import redirect_stdout
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tarfile
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('release_control', ROOT/'scripts/publish_release.py')
control = importlib.util.module_from_spec(spec)
spec.loader.exec_module(control)
COMMIT = 'a' * 40


class ReleaseTests(unittest.TestCase):
    def test_ref_and_commit_validation(self):
        control.validate_request('v0.1.0a1',COMMIT)
        for tag, sha in [('main',COMMIT),('v0.1.0',COMMIT),('v0.1.0a1;bad',COMMIT),('v0.1.0a1','main'),('v0.1.0a1','A'*40)]:
            with self.assertRaises(ValueError): control.validate_request(tag,sha)

    def test_version_asset_names_and_legacy_release(self):
        self.assertEqual(control.asset_names('0.1.0a2')[0],'azure_opsec_auditor-0.1.0a2-py3-none-any.whl')
        self.assertEqual(control.asset_names('0.1.0a1')[1],'azure_opsec_auditor-0.1.0a1.tar.gz')
        control.validate_request('v0.1.0a2',COMMIT)
        for value in ('../bad','0.1.0','0.1.0a2;bad'):
            with self.assertRaises(ValueError):control.asset_names(value)

    def test_local_tag_version_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            source=Path(temp)
            (source/'pyproject.toml').write_text('[project]\nversion = "0.1.0a2"\n')
            with patch.object(control,'command',return_value=COMMIT):
                self.assertEqual(control.verify_local(source,'v0.1.0a2',COMMIT),'0.1.0a2')
                with self.assertRaises(ValueError):control.verify_local(source,'v0.1.0a1',COMMIT)

    def test_annotated_remote_tag_and_changed_commit(self):
        replies=[json.dumps({'object':{'type':'tag','sha':'b'*40}}),json.dumps({'object':{'type':'commit','sha':COMMIT}})]
        with patch.object(control,'gh',side_effect=replies): control.verify_remote_tag('v0.1.0a1',COMMIT)
        with patch.object(control,'gh',return_value=json.dumps({'object':{'type':'commit','sha':'c'*40}})):
            with self.assertRaises(ValueError): control.verify_remote_tag('v0.1.0a1',COMMIT)

    def make_assets(self, dist):
        for name in control.ASSETS[:-1]: (dist/name).write_bytes(name.encode())
        (dist/'SHA256SUMS').write_text(''.join(f'{hashlib.sha256((dist/n).read_bytes()).hexdigest()}  {n}\n' for n in control.ASSETS[:-1]))

    def test_download_manifest_detects_tampering(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            source,target=Path(a),Path(b);self.make_assets(source)
            for p in source.iterdir(): shutil.copy2(p,target/p.name)
            control.verify_downloads(source,target)
            (target/control.ASSETS[0]).write_bytes(b'changed')
            with self.assertRaises(ValueError): control.verify_downloads(source,target)

    def test_existing_unexpected_asset_never_publishes(self):
        metadata=dict(isDraft=True,isPrerelease=True,targetCommitish=COMMIT,assets=[dict(name='unexpected')],url='synthetic')
        with patch.object(control,'verify_local',return_value='0.1.0a2'),patch.object(control,'verify_remote_tag'),patch.object(control,'gh',return_value=json.dumps(metadata)) as gh:
            with self.assertRaises(ValueError): control.publish(Path('.'),Path('.'),'v0.1.0a2',COMMIT)
            self.assertEqual(gh.call_count,1)

    def test_upload_failure_never_publishes(self):
        metadata=dict(isDraft=True,isPrerelease=True,targetCommitish=COMMIT,assets=[],url='synthetic')
        with patch.object(control,'verify_local',return_value='0.1.0a2'),patch.object(control,'verify_remote_tag'),patch.object(control,'gh',side_effect=[json.dumps(metadata),RuntimeError('upload failed')]) as gh:
            with self.assertRaises(RuntimeError): control.publish(Path('.'),Path('.'),'v0.1.0a2',COMMIT)
            self.assertFalse(any('edit' in call.args for call in gh.call_args_list))

    def test_verified_assets_publish_once_and_retry_is_read_only(self):
        with tempfile.TemporaryDirectory() as temp:
            dist=Path(temp);self.make_assets(dist)
            state=dict(isDraft=True,isPrerelease=True,targetCommitish=COMMIT,assets=[],url='synthetic')
            calls=[]
            def fake_gh(*args):
                calls.append(args)
                if args[:2]==('release','view'): return json.dumps(state)
                if args[:2]==('release','upload'):
                    state['assets'].append(dict(name=Path(args[3]).name));return ''
                if args[:2]==('release','download'):
                    target=Path(args[args.index('--dir')+1])
                    for asset in state['assets']:
                        shutil.copy2(dist/asset['name'],target/asset['name'])
                    return ''
                if args[:2]==('release','edit'):
                    state['isDraft']=False;return ''
                raise AssertionError('Unexpected release command')
            with redirect_stdout(io.StringIO()),patch.object(control,'verify_local',return_value='0.1.0a2'),patch.object(control,'verify_remote_tag'),patch.object(control,'gh',side_effect=fake_gh):
                control.publish(Path('.'),dist,'v0.1.0a2',COMMIT)
                self.assertEqual(len([c for c in calls if c[:2]==('release','upload')]),5)
                self.assertEqual(len([c for c in calls if c[:2]==('release','edit')]),1)
                calls.clear()
                control.publish(Path('.'),dist,'v0.1.0a2',COMMIT)
                self.assertFalse(any(c[:2] in [('release','upload'),('release','edit')] for c in calls))

    def test_archive_normalization_is_reproducible_and_preserves_content(self):
        with tempfile.TemporaryDirectory() as temp:
            dist=Path(temp)
            def containers(seed):
                with zipfile.ZipFile(dist/control.ASSETS[0],'w') as z:
                    z.writestr(zipfile.ZipInfo('module.py',(2026,1,seed,0,0,0)),b'print(1)\n')
                raw=io.BytesIO()
                with tarfile.open(fileobj=raw,mode='w') as t:
                    info=tarfile.TarInfo('package/module.py');info.size=9;info.mtime=seed
                    t.addfile(info,io.BytesIO(b'print(1)\n'))
                with (dist/control.ASSETS[1]).open('wb') as stream,gzip.GzipFile(fileobj=stream,mode='wb',mtime=seed) as z:
                    z.write(raw.getvalue())
            containers(1);control.normalize_archives(dist,1760000000)
            first=[(dist/n).read_bytes() for n in control.ASSETS[:2]]
            containers(2);control.normalize_archives(dist,1760000000)
            self.assertEqual(first,[(dist/n).read_bytes() for n in control.ASSETS[:2]])
            with zipfile.ZipFile(dist/control.ASSETS[0]) as z:self.assertEqual(z.read('module.py'),b'print(1)\n')
            with tarfile.open(dist/control.ASSETS[1]) as t:self.assertEqual(t.extractfile('package/module.py').read(),b'print(1)\n')


if __name__=='__main__':unittest.main()
