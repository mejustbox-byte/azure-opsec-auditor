"""JSON Schema artifact and dependency-free validator for its restricted subset."""
from datetime import datetime, timezone
import json
import os
import stat
import re
from .catalog import RULES

MAX_BYTES = 5 * 1024 * 1024
IDENTIFIER = {'type': 'string', 'pattern': '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$'}



DESCRIPTIONS = {
    'privileged': 'Утверждение о привилегированном доступе сущности.',
    'assignment': 'Тип назначения: постоянное, допустимое к активации или активное.',
    'scope_level': 'Нормализованный уровень области назначения.',
    'plane': 'Плоскость управления PIM: Entra или Azure.',
    'approval_required': 'Требуется ли одобрение активации.',
    'mfa_required': 'Требуется ли MFA при активации.',
    'max_activation_hours': 'Максимальная длительность активации в часах.',
    'state': 'Состояние политики CA; report_only не означает применение.',
    'privileged_target_included': 'Включена ли нормализованная привилегированная цель.',
    'privileged_target_excluded': 'Исключена ли нормализованная привилегированная цель.',
    'privileged_target': 'Является ли цель привилегированной.',
    'strength': 'Нормализованная требуемая сила аутентификации.',
    'enforced': 'Утверждение о применении требования; реальные сессии не проверяются.',
    'owner_count': 'Число ответственных владельцев сущности.',
    'credential_expired': 'Есть ли истёкшие учётные данные по метаданным без чтения значений.',
    'grant_type': 'Тип OAuth grant: application или delegated.',
    'permissions': 'Разрешённые имена permissions, нормализованные оператором.',
    'kind': 'Тип identity: managed или federated.',
    'broad_privilege': 'Есть ли широкие привилегии identity.',
    'issuer_trusted': 'Утверждение оператора о доверии issuer.',
    'subject_exact': 'Утверждение о точном соответствии subject.',
    'audience_expected': 'Соответствует ли audience ожидаемой.',
    'public_network_access': 'Разрешён ли публичный сетевой доступ.',
    'default_action': 'Сетевое действие по умолчанию: allow или deny.',
    'soft_delete': 'Включено ли обратимое удаление.',
    'purge_protection': 'Включена ли защита окончательного удаления.',
    'allow_blob_public_access': 'Разрешает ли account анонимный доступ к blob.',
    'container_access': 'Настроенный уровень анонимного доступа контейнера.',
    'direction': 'Направление сетевого правила.',
    'action': 'Действие сетевого правила.',
    'any_source': 'Допускается ли любой источник.',
    'ports': 'Список нормализованных портов; 0 означает все порты.',
    'enabled': 'Включено ли журналирование.',
    'destination_configured': 'Настроено ли назначение журналов; доставка не подтверждается.',
    'retention_days': 'Срок хранения журналов в днях.',
    'policy_configured': 'Настроена ли политика резервного копирования.',
    'last_backup': 'Последний статус копирования; фактический restore не подтверждается.',
}


class InputError(ValueError):
    """Safe validation error: never includes a supplied value or payload."""


def timestamp(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', value):
        raise InputError('Дата должна иметь формат UTC YYYY-MM-DDTHH:MM:SSZ')
    try:
        return datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    except ValueError:
        raise InputError('Неверная календарная дата') from None


def object_schema(properties, required):
    return {'type': 'object', 'properties': properties, 'required': required, 'additionalProperties': False}


def build_schema():
    sections = {}
    for rule in RULES:
        fields = {k: {'anyOf': [v, {'type': 'null'}], 'description': DESCRIPTIONS[k]} for k, v in rule.fields.items()}
        record = object_schema({'id': {**IDENTIFIER, 'description': 'Уникальный внутри раздела псевдоним записи; без реальных идентификаторов.'}, **fields}, ['id'])
        section = object_schema({
            'status': {'type': 'string', 'enum': ['complete', 'partial', 'unavailable', 'not_run'], 'description': 'Статус сбора; complete утверждает оператор, независимой проверки нет.'},
            'source': {**IDENTIFIER, 'description': 'Псевдоним источника нормализации.'}, 'api_version': {**IDENTIFIER, 'description': 'Версия API или синтетической нормализации.'},
            'records': {'type': 'array', 'items': record, 'maxItems': 1000, 'description': 'Не более 1000 записей; unavailable/not_run требуют пустого списка.'},
        }, ['status', 'source', 'api_version', 'records'])
        section['allOf'] = [{'if': {'properties': {'status': {'enum': ['unavailable', 'not_run']}}},
                             'then': {'properties': {'records': {'maxItems': 0}}}}]
        sections[rule.section] = section
    return {'$schema': 'https://json-schema.org/draft/2020-12/schema',
            '$id': 'https://github.com/mejustbox-byte/azure-opsec-auditor/blob/main/schemas/snapshot-v1.json',
            'title': 'Нормализованный локальный снимок v1',
            **object_schema({
                'schema_version': {'type': 'integer', 'const': 1, 'description': 'Версия входного контракта; поддерживается только 1.'},
                'synthetic': {'type': 'boolean', 'description': 'true для синтетического примера; false не доказывает реальную платформенную проверку.'},
                'scope': {**IDENTIFIER, 'description': 'Псевдоним области снимка без реальных tenant identifiers.'},
                'collected_at': {'type': 'string', 'description': 'Самое раннее время включённых наблюдений в UTC.', 'format': 'date-time', 'pattern': '^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$'},
                'sections': object_schema(sections, []),
            }, ['schema_version', 'synthetic', 'scope', 'collected_at', 'sections'])}


SCHEMA = build_schema()


def check(value, spec, path='snapshot'):
    # path consists only of our schema keys and numeric indices, never input keys.
    if 'anyOf' in spec:
        for choice in spec['anyOf']:
            try:
                check(value, choice, path)
                return
            except InputError:
                pass
        raise InputError(f'{path}: неверный тип или значение поля')
    kind = spec.get('type')
    matches = {'object': type(value) is dict, 'array': type(value) is list,
               'integer': type(value) is int, 'boolean': type(value) is bool,
               'string': type(value) is str, 'null': value is None}
    if kind and not matches[kind]:
        raise InputError(f'{path}: ожидается {kind}')
    if 'const' in spec and value != spec['const']:
        raise InputError(f'{path}: неподдерживаемая версия')
    if 'enum' in spec and value not in spec['enum']:
        raise InputError(f'{path}: недопустимое значение enum')
    if kind == 'object':
        if any(k not in spec['properties'] for k in value):
            raise InputError(f'{path}: неизвестные поля запрещены')
        if any(k not in value for k in spec['required']):
            raise InputError(f'{path}: обязательное поле отсутствует')
        for key in spec['properties']:
            if key in value:
                check(value[key], spec['properties'][key], f'{path}.{key}')
    elif kind == 'array':
        if len(value) > spec.get('maxItems', 1000):
            raise InputError(f'{path}: слишком много элементов')
        if spec.get('uniqueItems') and len({json.dumps(v, sort_keys=True) for v in value}) != len(value):
            raise InputError(f'{path}: повторяющиеся элементы')
        for index, item in enumerate(value):
            check(item, spec['items'], f'{path}[{index}]')
    elif kind == 'integer':
        if not spec.get('minimum', value) <= value <= spec.get('maximum', value):
            raise InputError(f'{path}: целое число вне допустимого диапазона')
    elif kind == 'string':
        if 'pattern' in spec and not re.fullmatch(spec['pattern'], value, flags=re.ASCII):
            raise InputError(f'{path}: неверный синтаксис строки')
        if spec.get('format') == 'date-time':
            timestamp(value)


def validate(data):
    check(data, SCHEMA)
    for section in data['sections'].values():
        if section['status'] in ('unavailable', 'not_run') and section['records']:
            raise InputError('Источник unavailable/not_run не должен содержать записи')
        ids = [r['id'] for r in section['records']]
        if len(ids) != len(set(ids)):
            raise InputError('Повторяющиеся идентификаторы записей внутри раздела')
    return data


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InputError('Повторяющийся ключ JSON')
        result[key] = value
    return result


def reject_constant(_):
    raise InputError('Неконечные числовые значения JSON запрещены')


def load(path):
    fd = None
    try:
        # Nonblocking open avoids hanging on a FIFO before we can inspect its type.
        flags = os.O_RDONLY | getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_BINARY', 0)
        fd = os.open(os.fspath(path), flags)
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise InputError('Входной снимок должен быть обычным файлом')
        with os.fdopen(fd, 'rb') as stream:
            fd = None  # The stream now owns and closes the descriptor.
            payload = stream.read(MAX_BYTES + 1)
        if len(payload) > MAX_BYTES:
            raise InputError('Размер ввода превышает 5 MiB')
        data = json.loads(payload.decode('utf-8'), object_pairs_hook=unique_object,
                          parse_constant=reject_constant)
        return validate(data)
    except InputError:
        raise
    except (OSError, UnicodeError, ValueError, RecursionError):
        raise InputError('Не удалось прочитать корректный JSON-снимок в UTF-8') from None
    finally:
        if fd is not None:
            os.close(fd)
