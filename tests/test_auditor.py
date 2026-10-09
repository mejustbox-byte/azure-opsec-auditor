import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from azure_opsec_auditor.catalog import RULES
from azure_opsec_auditor.engine import audit, markdown
from azure_opsec_auditor.schema import InputError, MAX_BYTES, SCHEMA, load, validate

ROOT = Path(__file__).resolve().parents[1]
AS_OF = '2026-10-09T12:00:00Z'


def fixture(name='good'):
    return load(ROOT / 'fixtures' / f'{name}.json')


class RuleTests(unittest.TestCase):
    def test_each_rule_good_bad_unknown_not_run(self):
        for name, expected in [('good','pass'),('bad','fail'),('unknown','unknown'),('not_run','not_run')]:
            report = audit(fixture(name), as_of=AS_OF)
            self.assertEqual(len(report['findings']), 12)
            self.assertEqual({f['rule_id'] for f in report['findings']}, {r.id for r in RULES})
            for finding in report['findings']:
                with self.subTest(scenario=name,rule=finding['rule_id']):
                    self.assertEqual(finding['status'],expected)
                    self.assertTrue(finding['remediation'])
                    self.assertTrue(finding['limitations'])
                    self.assertIn(finding['severity'], ('medium','high'))
                    self.assertEqual(finding['source'],'synthetic-fixture')
            self.assertEqual(report['exit_code'], {'good':0,'bad':1,'unknown':2,'not_run':2}[name])

    def test_missing_evidence_each_required_field(self):
        for rule in RULES:
            for key in rule.fields:
                data = fixture()
                del data['sections'][rule.section]['records'][0][key]
                report = audit(data, as_of=AS_OF)
                finding = next(f for f in report['findings'] if f['rule_id'] == rule.id)
                self.assertEqual(finding['status'],'unknown', (rule.id,key))
                self.assertEqual(report['exit_code'],2)

    def test_empty_missing_unavailable_and_partial(self):
        for status in ('complete','partial','unavailable','not_run','missing'):
            data=fixture()
            if status=='missing':
                del data['sections']['storage']
            else:
                data['sections']['storage'].update(status=status, records=[])
            r=audit(data,as_of=AS_OF)
            f=next(f for f in r['findings'] if f['rule_id']=='ST-01')
            self.assertEqual(f['status'],'not_run' if status in ('missing','not_run') else 'unknown')
            self.assertEqual(r['exit_code'],2)

    def test_partial_keeps_failure_but_never_full_coverage(self):
        data=fixture('bad')
        data['sections']['storage']['status']='partial'
        r=audit(data,as_of=AS_OF)
        self.assertEqual({f['status'] for f in r['findings'] if f['rule_id']=='ST-01'}, {'fail','unknown'})
        self.assertEqual(r['exit_code'],2)

    def test_age_budget_future_and_historical_replay(self):
        self.assertEqual(audit(fixture(),as_of='2026-10-16T00:00:00Z')['exit_code'],0)
        self.assertEqual(audit(fixture(),as_of='2026-10-16T00:00:01Z')['summary']['unknown'],12)
        with self.assertRaises(InputError): audit(fixture(),as_of='2026-10-08T00:00:00Z')
        with self.assertRaises(InputError): audit(fixture(),as_of=AS_OF,max_age_days=0)

    def test_determinism_and_no_mutation(self):
        data=fixture('mixed'); original=copy.deepcopy(data)
        first=audit(data,as_of=AS_OF); second=audit(data,as_of=AS_OF)
        self.assertEqual(first,second); self.assertEqual(data,original)
        self.assertIn('NOT VERIFIED',markdown(first))
        self.assertIn('Remediation:',markdown(first))
        self.assertEqual(first['summary'],{'pass':3,'fail':3,'unknown':3,'not_run':3})

    def test_rule_boundaries(self):
        cases=[
            ('rbac',dict(privileged=True,scope_level='resource'),'pass'),
            ('rbac',dict(privileged=True,scope_level='subscription',assignment='eligible'),'pass'),
            ('pim',dict(max_activation_hours=0),'fail'),
            ('pim',dict(max_activation_hours=8),'pass'),
            ('pim',dict(max_activation_hours=9),'fail'),
            ('pim',dict(mfa_required=False),'fail'),
            ('conditional_access',dict(privileged_target_excluded=True),'fail'),
            ('conditional_access',dict(privileged_target_included=False),'fail'),
            ('mfa',dict(enforced=False),'fail'),
            ('mfa',dict(privileged_target=False,enforced=False),'pass'),
            ('service_principals',dict(credential_expired=True),'fail'),
            ('service_principals',dict(privileged=False,owner_count=0),'pass'),
            ('oauth',dict(grant_type='delegated',permissions=['Directory.ReadWrite.All']),'pass'),
            ('identities',dict(kind='managed',issuer_trusted=False,subject_exact=False,audience_expected=False),'pass'),
            ('identities',dict(broad_privilege=True),'fail'),
            ('identities',dict(issuer_trusted=False),'fail'),
            ('key_vault',dict(public_network_access=True,default_action='deny'),'pass'),
            ('key_vault',dict(public_network_access=True,default_action='allow'),'fail'),
            ('key_vault',dict(soft_delete=False),'fail'),
            ('storage',dict(allow_blob_public_access=False,container_access='container'),'pass'),
            ('storage',dict(allow_blob_public_access=True,container_access='private'),'pass'),
            ('network',dict(any_source=True,ports=[443]),'pass'),
            ('network',dict(any_source=True,ports=[0]),'fail'),
            ('network',dict(any_source=True,direction='outbound'),'pass'),
            ('network',dict(any_source=True,action='deny'),'pass'),
            ('logging',dict(retention_days=29),'fail'),
            ('logging',dict(retention_days=30),'pass'),
            ('logging',dict(destination_configured=False),'fail'),
            ('recovery',dict(policy_configured=False),'fail'),
        ]
        for section, fields, expected in cases:
            with self.subTest(section=section,fields=fields):
                data=fixture(); data['sections'][section]['records'][0].update(fields)
                result=audit(data,as_of=AS_OF)
                rid=next(r.id for r in RULES if r.section==section)
                self.assertEqual(next(f['status'] for f in result['findings'] if f['rule_id']==rid),expected)

    def test_offline_no_socket(self):
        with patch('socket.socket', side_effect=AssertionError('Network forbidden')):
            self.assertEqual(audit(fixture(),as_of=AS_OF)['exit_code'],0)


class ValidationTests(unittest.TestCase):
    def test_schema_artifact_in_sync(self):
        self.assertEqual(json.loads((ROOT/'schemas/snapshot-v1.json').read_text()),SCHEMA)

    def test_invalid_shapes_types_and_ranges(self):
        mutations=[lambda d:d.update(schema_version=True), lambda d:d.update(schema_version=2),
                   lambda d:d.update(synthetic='true'),lambda d:d.update(secret='DO_NOT_ECHO'),
                   lambda d:d.update(scope='unsafe|<script>'), lambda d:d.update(collected_at='2026-02-30T00:00:00Z'),
                   lambda d:d['sections']['pim']['records'][0].update(max_activation_hours=True),
                   lambda d:d['sections']['network']['records'][0].update(ports=[65536]),
                   lambda d:d['sections']['network']['records'][0].update(ports=[22,22]),
                   lambda d:d['sections']['storage']['records'][0].update(container_access='invalid'),
                   lambda d:d['sections']['storage'].update(status='unavailable'),
                   lambda d:d['sections']['storage']['records'].append(d['sections']['storage']['records'][0]),
                   lambda d:d['sections']['storage']['records'][0].update(id='injected\ntext')]
        for mutation in mutations:
            data=fixture(); mutation(data)
            with self.assertRaises(InputError): validate(data)
        for invalid in ([],None,{'sections':{}},42):
            with self.assertRaises(InputError): validate(invalid)

    def test_untrusted_values_never_echoed(self):
        data=fixture(); data['scope']='DO_NOT_ECHO <script>'
        with self.assertRaises(InputError) as exc: validate(data)
        self.assertNotIn('DO_NOT_ECHO',str(exc.exception))

    def test_parser_failures(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'input.json'
            for raw in (b'{"x":1,"x":2}', b'NaN', b'Infinity', b'\xff',b'{',b'['*2000+b']'*2000,b' '* (MAX_BYTES+1)):
                path.write_bytes(raw)
                with self.assertRaises(InputError): load(path)
            with self.assertRaises(InputError): load(Path(temp)/'missing')

    def test_strict_limits(self):
        data=fixture(); data['sections']['storage']['records']=[dict(id=f'synthetic:{n}') for n in range(1001)]
        with self.assertRaises(InputError): validate(data)
        data=fixture(); data['sections']['oauth']['records'][0]['permissions']=['User.Read']*51
        with self.assertRaises(InputError): validate(data)


class CLITests(unittest.TestCase):
    def run_cli(self,*args):
        return subprocess.run([sys.executable,'-m','azure_opsec_auditor',*map(str,args)],cwd=ROOT,capture_output=True,text=True)

    def test_json_markdown_and_exit_codes(self):
        for name, code in [('good',0),('bad',1),('mixed',2),('unknown',2),('not_run',2)]:
            p=self.run_cli(ROOT/'fixtures'/f'{name}.json','--as-of',AS_OF)
            self.assertEqual(p.returncode,code,p.stderr)
            self.assertEqual(json.loads(p.stdout)['exit_code'],code)
            self.assertEqual(p.stderr,'')
        p=self.run_cli(ROOT/'fixtures/mixed.json','--as-of',AS_OF,'--format','markdown')
        self.assertEqual(p.returncode,2); self.assertIn('# Azure',p.stdout)

    def test_error_no_traceback_or_payload(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'input.json'; path.write_text('{"DO_NOT_ECHO":"SECRET"}')
            p=self.run_cli(path)
            self.assertEqual(p.returncode,2); self.assertEqual(p.stdout,'')
            self.assertNotIn('DO_NOT_ECHO',p.stderr); self.assertNotIn('SECRET',p.stderr)
            self.assertNotIn('Traceback',p.stderr)
        p=self.run_cli(ROOT/'fixtures/good.json','--as-of','invalid')
        self.assertEqual(p.returncode,2); self.assertNotIn('Traceback',p.stderr)

    def test_help_version(self):
        for flag in ('--help','--version'):
            self.assertEqual(self.run_cli(flag).returncode,0)


if __name__=='__main__': unittest.main()
