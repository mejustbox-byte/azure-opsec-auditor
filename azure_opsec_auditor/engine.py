"""Pure rules with explicit coverage; pass is never a tenant-wide assurance."""
import json
from datetime import datetime, timezone, timedelta
from . import __version__
from .catalog import RULES
from .schema import InputError, timestamp, validate


def audit(snapshot, *, as_of=None, max_age_days=7):
    validate(snapshot)
    if type(max_age_days) is not int or not 1 <= max_age_days <= 365:
        raise InputError('max_age_days должен быть от 1 до 365')
    now = timestamp(as_of) if as_of else datetime.now(timezone.utc).replace(microsecond=0)
    collected = timestamp(snapshot['collected_at'])
    if collected > now:
        raise InputError('Дата снимка находится в будущем')
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
            finding(rule, 'not_run', 'Источник не собирался.', source=section)
            continue
        if state == 'unavailable':
            finding(rule, 'unknown', 'Источник недоступен; разрешения, лицензии и сбор не проверены.', source=section)
            continue
        if stale:
            finding(rule, 'unknown', 'Снимок старше выбранного допустимого возраста.', source=section)
            continue
        if state == 'partial' or not section['records']:
            finding(rule, 'unknown', 'Сбор неполный или пустой; охват области установить нельзя.', source=section)
        for record in sorted(section['records'], key=lambda r: r['id']):
            if any(record.get(k) is None for k in rule.fields):
                finding(rule, 'unknown', 'Обязательные нормализованные данные отсутствуют либо равны null.', record, section)
            else:
                unsafe = rule.unsafe(record)
                finding(rule, 'fail' if unsafe else 'pass',
                        'Условие риска обнаружено в предоставленных метаданных.' if unsafe else 'Условие риска для этой записи не обнаружено.', record, section)
    counts = {s: sum(f['status'] == s for f in findings) for s in ('pass', 'fail', 'unknown', 'not_run')}
    code = 2 if counts['unknown'] or counts['not_run'] else 1 if counts['fail'] else 0
    return {'report_version': 1, 'tool_version': __version__, 'mode': 'offline',
            'synthetic': snapshot['synthetic'], 'scope': snapshot['scope'],
            'as_of': now.strftime('%Y-%m-%dT%H:%M:%SZ'), 'max_age_days': max_age_days,
            'platform_validation': 'НЕ ПРОВЕРЕНО: Azure/Entra, разрешения, сбор и восстановление',
            'summary': counts, 'exit_code': code, 'coverage': coverage, 'findings': findings}


def markdown(report):
    lines = ['# Локальный отчёт о безопасности Azure / Entra', '',
             f"Область: `{report['scope']}` | synthetic: `{str(report['synthetic']).lower()}` | время оценки: `{report['as_of']}`", '',
             report['platform_validation'], '',
             'pass относится только к переданной записи и узкому правилу. Безопасность tenant целиком не подтверждается.', '',
             'Итог: ' + ', '.join(f'{k}={v}' for k, v in report['summary'].items()), '',
             '| Правило | Статус источника | Записи |', '|---|---|---:|']
    for rule, c in report['coverage'].items():
        lines.append(f"| {rule} | {c['source_status']} | {c['records']} |")
    for f in report['findings']:
        lines += ['', f"## {f['rule_id']} / {f['resource_ref']}: {f['status']} ({f['severity']})", '',
                  f['title'], '', f['reason'], '',
                  f"Источник: `{f['source']}` / API: `{f['api_version']}` / наблюдение: `{f['collected_at']}`", '',
                  'Данные: `' + json.dumps(f['evidence'], sort_keys=True) + '`', '',
                  'Рекомендация: ' + f['remediation'], '', 'Ограничения: ' + f['limitations']]
    return '\n'.join(lines) + '\n'
