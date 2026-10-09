"""Регрессии: декларация MIT не заменяет фактические тексты в пакете."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('distribution_verify', ROOT/'scripts/verify_distribution.py')
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


class LicenseTests(unittest.TestCase):
    def write_wheel(self, path, *, missing=False, changed=False, expression='MIT'):
        prefix = 'synthetic-0.1.0.dist-info/'
        with zipfile.ZipFile(path, 'w') as archive:
            archive.writestr(prefix+'METADATA', f'Metadata-Version: 2.4\nLicense-Expression: {expression}\nLicense-File: LICENSE\nLicense-File: LICENSE.ru.md\n')
            archive.writestr(prefix+'licenses/LICENSE', b'changed' if changed else (ROOT/'LICENSE').read_bytes())
            if not missing:
                archive.writestr(prefix+'licenses/LICENSE.ru.md', (ROOT/'LICENSE.ru.md').read_bytes())

    def test_missing_or_changed_license_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'synthetic.whl'
            self.write_wheel(path, missing=True)
            with self.assertRaises(KeyError): verify.verify_license(path)
            self.write_wheel(path, changed=True)
            with self.assertRaises(RuntimeError): verify.verify_license(path)

    def test_wrong_license_metadata_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'synthetic.whl'
            self.write_wheel(path, expression='Apache-2.0')
            with self.assertRaises(RuntimeError): verify.verify_license(path)


if __name__ == '__main__':
    unittest.main()
