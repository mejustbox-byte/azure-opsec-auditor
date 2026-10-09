"""Pure rules with explicit coverage; pass is never a tenant-wide assurance."""
import json
from datetime import datetime, timezone, timedelta
from . import __version__
from .catalog import RULES
from .schema import InputError, timestamp, validate


def audit(snapshot, *, as_of=None, max_age_days=7):
    validate(snapshot)
    if type(max_age_days) is not int or not 1 <= max_age_days <= 365:
        raise InputError('max_age_days must be between 1 and 365')
    now = timestamp(as_of) if as_of else datetime.now(timezone.utc).replace(microsecond=0)
    collected = timestamp(snapshot['collected_at'])
    if collected > now:
        raise InputError('Snapshot timestamp is in the future')
    stale = now - collected > timedelta(days=max_age_days)
    findings = []
    coverage = {}

    def finding(rule, status, reason, record=None, source=None):
        fields = {k: record[k] for k in rule.fields if record is not None and k in record}
        findings.append({
            'rule_id': rule.id, 'rule_version': 1, 'title': rule.title,
            'resource_ref': record['id'] if record is not None else 'coverage',
            'status': status, 'severity': rule.severity,
            'confidence': 'normalized_metadata' if status in ('pass', 'fail') else 'insufficient_evidence',
            'evidence': fields, 'source': source['source'] if source else None,
            'api_version': source['api_version'] if source else None,
            'collected_at': snapshot['collected_at'], 'reason': reason,
            'remediation': rule.remediation, 'limitations': rule.limitation,
        })

    for rule in RULES:
        section = snapshot['sections'].get(rule.section)
        state = section['status'] if section else 'not_run'
        coverage[rule.id] = {'section': rule.section, 'source_status': state,
                             'records': len(section['records']) if section else 0}
        if state == 'not_run':
            finding(rule, 'not_run', 'Source was not collected.', source=section)
            continue
        if state == 'unavailable':
            finding(rule, 'unknown', 'Source unavailable; permissions/licensing/collection not verified.', source=section)
            continue
        if stale:
            finding(rule, 'unknown', 'Snapshot exceeds the selected freshness budget.', source=section)
            continue
        if state == 'partial' or not section['records']:
            finding(rule, 'unknown', 'Collection incomplete or empty; scope coverage cannot be established.', source=section)
        for record in sorted(section['records'], key=lambda r: r['id']):
            if any(record.get(k) is None for k in rule.fields):
                finding(rule, 'unknown', 'Required normalized evidence missing or null.', record, section)
            else:
                unsafe = rule.unsafe(record)
                finding(rule, 'fail' if unsafe else 'pass',
                        'Risk condition observed in supplied metadata.' if unsafe else 'Risk condition not observed for this record.', record, section)
    counts = {s: sum(f['status'] == s for f in findings) for s in ('pass', 'fail', 'unknown', 'not_run')}
    code = 2 if counts['unknown'] or counts['not_run'] else 1 if counts['fail'] else 0
    return {'report_version': 1, 'tool_version': __version__, 'mode': 'offline',
            'synthetic': snapshot['synthetic'], 'scope': snapshot['scope'],
            'as_of': now.strftime('%Y-%m-%dT%H:%M:%SZ'), 'max_age_days': max_age_days,
            'platform_validation': 'NOT VERIFIED: Azure/Entra, permissions, collection and restore',
            'summary': counts, 'exit_code': code, 'coverage': coverage, 'findings': findings}


def markdown(report):
    lines = ['# Azure / Entra offline posture report', '',
             f"Scope: `{report['scope']}` | synthetic: `{str(report['synthetic']).lower()}` | as of: `{report['as_of']}`", '',
             report['platform_validation'], '',
             'Pass applies only to the supplied record and narrow rule. This is not tenant-wide assurance.', '',
             'Summary: ' + ', '.join(f'{k}={v}' for k, v in report['summary'].items()), '',
             '| Rule | Source status | Records |', '|---|---|---:|']
    for rule, c in report['coverage'].items():
        lines.append(f"| {rule} | {c['source_status']} | {c['records']} |")
    for f in report['findings']:
        lines += ['', f"## {f['rule_id']} / {f['resource_ref']}: {f['status']} ({f['severity']})", '',
                  f['title'], '', f['reason'], '',
                  f"Source: `{f['source']}` / API: `{f['api_version']}` / observed: `{f['collected_at']}`", '',
                  'Evidence: `' + json.dumps(f['evidence'], sort_keys=True) + '`', '',
                  'Remediation: ' + f['remediation'], '', 'Limitations: ' + f['limitations']]
    return '\n'.join(lines) + '\n'
