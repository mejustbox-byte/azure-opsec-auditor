"""JSON Schema artifact and dependency-free validator for its restricted subset."""
from datetime import datetime, timezone
import json
import os
import stat
import re
from .catalog import RULES

MAX_BYTES = 5 * 1024 * 1024
IDENTIFIER = {'type': 'string', 'pattern': '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$'}


class InputError(ValueError):
    """Safe validation error: never includes a supplied value or payload."""


def timestamp(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', value):
        raise InputError('Timestamp must be UTC YYYY-MM-DDTHH:MM:SSZ')
    try:
        return datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    except ValueError:
        raise InputError('Invalid calendar timestamp') from None


def object_schema(properties, required):
    return {'type': 'object', 'properties': properties, 'required': required, 'additionalProperties': False}


def build_schema():
    sections = {}
    for rule in RULES:
        fields = {k: {'anyOf': [v, {'type': 'null'}]} for k, v in rule.fields.items()}
        record = object_schema({'id': IDENTIFIER, **fields}, ['id'])
        section = object_schema({
            'status': {'type': 'string', 'enum': ['complete', 'partial', 'unavailable', 'not_run']},
            'source': IDENTIFIER, 'api_version': IDENTIFIER,
            'records': {'type': 'array', 'items': record, 'maxItems': 1000},
        }, ['status', 'source', 'api_version', 'records'])
        section['allOf'] = [{'if': {'properties': {'status': {'enum': ['unavailable', 'not_run']}}},
                             'then': {'properties': {'records': {'maxItems': 0}}}}]
        sections[rule.section] = section
    return {'$schema': 'https://json-schema.org/draft/2020-12/schema',
            '$id': 'https://github.com/mejustbox-byte/azure-opsec-auditor/blob/main/schemas/snapshot-v1.json',
            'title': 'Normalized offline snapshot v1',
            **object_schema({
                'schema_version': {'type': 'integer', 'const': 1},
                'synthetic': {'type': 'boolean'},
                'scope': IDENTIFIER,
                'collected_at': {'type': 'string', 'format': 'date-time', 'pattern': '^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$'},
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
        raise InputError(f'{path}: invalid field type or value')
    kind = spec.get('type')
    matches = {'object': type(value) is dict, 'array': type(value) is list,
               'integer': type(value) is int, 'boolean': type(value) is bool,
               'string': type(value) is str, 'null': value is None}
    if kind and not matches[kind]:
        raise InputError(f'{path}: expected {kind}')
    if 'const' in spec and value != spec['const']:
        raise InputError(f'{path}: unsupported version')
    if 'enum' in spec and value not in spec['enum']:
        raise InputError(f'{path}: invalid enum value')
    if kind == 'object':
        if any(k not in spec['properties'] for k in value):
            raise InputError(f'{path}: unknown fields are prohibited')
        if any(k not in value for k in spec['required']):
            raise InputError(f'{path}: required field missing')
        for key in spec['properties']:
            if key in value:
                check(value[key], spec['properties'][key], f'{path}.{key}')
    elif kind == 'array':
        if len(value) > spec.get('maxItems', 1000):
            raise InputError(f'{path}: too many items')
        if spec.get('uniqueItems') and len({json.dumps(v, sort_keys=True) for v in value}) != len(value):
            raise InputError(f'{path}: duplicate items')
        for index, item in enumerate(value):
            check(item, spec['items'], f'{path}[{index}]')
    elif kind == 'integer':
        if not spec.get('minimum', value) <= value <= spec.get('maximum', value):
            raise InputError(f'{path}: integer outside allowed range')
    elif kind == 'string':
        if 'pattern' in spec and not re.fullmatch(spec['pattern'], value, flags=re.ASCII):
            raise InputError(f'{path}: invalid string syntax')
        if spec.get('format') == 'date-time':
            timestamp(value)


def validate(data):
    check(data, SCHEMA)
    for section in data['sections'].values():
        if section['status'] in ('unavailable', 'not_run') and section['records']:
            raise InputError('Unavailable/not_run source must not contain records')
        ids = [r['id'] for r in section['records']]
        if len(ids) != len(set(ids)):
            raise InputError('Duplicate record identifiers within a section')
    return data


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InputError('Duplicate JSON object key')
        result[key] = value
    return result


def reject_constant(_):
    raise InputError('Non-finite JSON numbers are prohibited')


def load(path):
    fd = None
    try:
        # Nonblocking open avoids hanging on a FIFO before we can inspect its type.
        flags = os.O_RDONLY | getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_BINARY', 0)
        fd = os.open(os.fspath(path), flags)
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise InputError('Snapshot input must be a regular file')
        with os.fdopen(fd, 'rb') as stream:
            fd = None  # The stream now owns and closes the descriptor.
            payload = stream.read(MAX_BYTES + 1)
        if len(payload) > MAX_BYTES:
            raise InputError('Input exceeds 5 MiB limit')
        data = json.loads(payload.decode('utf-8'), object_pairs_hook=unique_object,
                          parse_constant=reject_constant)
        return validate(data)
    except InputError:
        raise
    except (OSError, UnicodeError, ValueError, RecursionError):
        raise InputError('Cannot read a valid UTF-8 JSON snapshot') from None
    finally:
        if fd is not None:
            os.close(fd)
