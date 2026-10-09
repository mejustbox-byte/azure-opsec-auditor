"""Versioned, intentionally narrow checks; no cloud transport or credentials."""
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Rule:
    id: str
    section: str
    title: str
    severity: str
    fields: dict
    unsafe: Callable[[dict], bool]
    remediation: str
    limitation: str


BOOL = {'type': 'boolean'}
COUNT = {'type': 'integer', 'minimum': 0, 'maximum': 1000000}

def enum(*values):
    return {'type': 'string', 'enum': list(values)}


RULES = (
    Rule('RBAC-01', 'rbac', 'Постоянное назначение широких привилегий', 'high',
         {'privileged': BOOL, 'assignment': enum('permanent', 'eligible', 'active'),
          'scope_level': enum('resource', 'resource_group', 'subscription', 'management_group', 'directory')},
         lambda x: x['privileged'] and x['assignment'] == 'permanent' and x['scope_level'] in ('subscription', 'management_group', 'directory'),
         'Пересмотрите широкие привилегии, уменьшите область доступа и при необходимости используйте ограниченную по времени допустимость активации.',
         'Оцениваются только нормализованные привилегии и область; группы, наследование и действия пользовательских ролей не раскрываются.'),
    Rule('PIM-01', 'pim', 'Защита активации привилегированного доступа', 'high',
         {'plane': enum('entra', 'azure'), 'approval_required': BOOL, 'mfa_required': BOOL,
          'max_activation_hours': {'type': 'integer', 'minimum': 0, 'maximum': 8760}},
         lambda x: not x['approval_required'] or not x['mfa_required'] or not 0 < x['max_activation_hours'] <= 8,
         'Пересмотрите политику активации: требуйте одобрение, MFA и положительную длительность не более восьми часов.',
         'Восемь часов — выбранный базовый предел, не гарантия Microsoft; допустимость и фактическая активация не собираются.'),
    Rule('CA-01', 'conditional_access', 'Заявленный охват привилегированной цели политикой CA', 'high',
         {'state': enum('enabled', 'report_only', 'disabled'), 'privileged_target_included': BOOL, 'privileged_target_excluded': BOOL},
         lambda x: x['state'] != 'enabled' or not x['privileged_target_included'] or x['privileged_target_excluded'],
         'Перед применением проверьте действующие политики для цели, исключения и аварийный доступ.',
         'Одна нормализованная запись цели и политики; эффективный охват и условия входа не вычисляются.'),
    Rule('MFA-01', 'mfa', 'Требование фишинг-устойчивой аутентификации для привилегированной цели', 'high',
         {'privileged_target': BOOL, 'strength': enum('phishing_resistant', 'mfa', 'single_factor'), 'enforced': BOOL},
         lambda x: x['privileged_target'] and (x['strength'] != 'phishing_resistant' or not x['enforced']),
         'Требуйте подходящую фишинг-устойчивую силу аутентификации для привилегированного доступа и проверьте исключения.',
         'Только утверждение о конфигурации; зарегистрированные методы и фактическое применение в сессиях не проверены.'),
    Rule('SP-01', 'service_principals', 'Привилегированная сущность без владельца или с истёкшими учётными данными', 'high',
         {'privileged': BOOL, 'owner_count': COUNT, 'credential_expired': BOOL},
         lambda x: x['privileged'] and (x['owner_count'] == 0 or x['credential_expired']),
         'Назначьте ответственных владельцев, пересмотрите привилегии и выведите истёкшие учётные данные из использования без экспорта значений.',
         'Только метаданные владельцев и срока действия; содержимое учётных данных, активность и достижимость не оцениваются.'),
    Rule('OAUTH-01', 'oauth', 'Выдача разрешений приложения с высоким риском', 'high',
         {'grant_type': enum('application', 'delegated'), 'permissions': {'type': 'array', 'items': {'type': 'string', 'pattern': '^[A-Za-z][A-Za-z0-9._-]{0,127}$'}, 'maxItems': 50, 'uniqueItems': True}},
         lambda x: x['grant_type'] == 'application' and bool(set(x['permissions']) & {'Directory.ReadWrite.All', 'RoleManagement.ReadWrite.Directory', 'AppRoleAssignment.ReadWrite.All', 'Application.ReadWrite.All', 'Mail.ReadWrite'}),
         'Проверьте согласие администратора и удалите ненужные разрешения приложения с высоким риском отдельным согласованным изменением.',
         'Явный ограниченный список риска, не полный перечень. Разрешённые имена permissions утверждает ввод; использование не проверяется.'),
    Rule('OIDC-01', 'identities', 'Привилегии и доверие управляемой или федеративной identity', 'high',
         {'kind': enum('managed', 'federated'), 'broad_privilege': BOOL, 'issuer_trusted': BOOL,
          'subject_exact': BOOL, 'audience_expected': BOOL},
         lambda x: x['broad_privilege'] or (x['kind'] == 'federated' and not (x['issuer_trusted'] and x['subject_exact'] and x['audience_expected'])),
         'Уменьшите привилегии identity и привяжите федерацию к проверенному issuer, точному subject и ожидаемой audience.',
         'Доверие нормализует оператор; issuer и правила конкретного провайдера не проверяются. Managed identities игнорируют флаги федерации.'),
    Rule('KV-01', 'key_vault', 'Сетевая открытость vault и защита удаления', 'high',
         {'public_network_access': BOOL, 'default_action': enum('allow', 'deny'), 'soft_delete': BOOL, 'purge_protection': BOOL},
         lambda x: (x['public_network_access'] and x['default_action'] == 'allow') or not x['soft_delete'] or not x['purge_protection'],
         'Пересмотрите сетевые ограничения vault, включите soft delete и purge protection согласованным изменением.',
         'Только конфигурация управления; секреты не читаются, эффективные RBAC, trusted services и DNS не проверяются.'),
    Rule('ST-01', 'storage', 'Анонимный доступ к контейнеру', 'high',
         {'allow_blob_public_access': BOOL, 'container_access': enum('private', 'blob', 'container')},
         lambda x: x['allow_blob_public_access'] and x['container_access'] != 'private',
         'После проверки требований приложения отключите ненужный анонимный доступ к blob и установите приватный доступ контейнера.',
         'Только настроенный анонимный доступ; blob не скачивается, сетевая достижимость не проверяется.'),
    Rule('NET-01', 'network', 'Неограниченное входящее правило для чувствительного порта', 'high',
         {'direction': enum('inbound', 'outbound'), 'action': enum('allow', 'deny'), 'any_source': BOOL,
          'ports': {'type': 'array', 'items': {'type': 'integer', 'minimum': 0, 'maximum': 65535}, 'maxItems': 50, 'uniqueItems': True}},
         lambda x: x['direction'] == 'inbound' and x['action'] == 'allow' and x['any_source'] and bool(set(x['ports']) & {0, 22, 3389, 1433, 3306, 5432}),
         'Ограничьте источники и чувствительные входящие порты; отдельно проверьте приоритеты NSG и топологию.',
         'В этой схеме порт 0 означает все порты. Приоритеты, диапазоны, ASG, маршруты и активная достижимость не анализируются.'),
    Rule('LOG-01', 'logging', 'Настройка диагностики и срок хранения', 'medium',
         {'enabled': BOOL, 'destination_configured': BOOL, 'retention_days': {'type': 'integer', 'minimum': 0, 'maximum': 36500}},
         lambda x: not x['enabled'] or not x['destination_configured'] or x['retention_days'] < 30,
         'Настройте необходимые журналы и назначение со сроком хранения не менее 30 дней либо документируйте согласованный базовый срок.',
         'Тридцать дней — базовое значение MVP. Конфигурация не подтверждает доставку или охват всего tenant.'),
    Rule('REC-01', 'recovery', 'Настройка резервного копирования и последний статус', 'high',
         {'policy_configured': BOOL, 'last_backup': enum('success', 'failed', 'never')},
         lambda x: not x['policy_configured'] or x['last_backup'] != 'success',
         'Проверьте охват резервного копирования и неудачные задания; проведите отдельно разрешённое упражнение восстановления.',
         'Свежесть последнего статуса ограничена лишь возрастом снимка; восстановление и содержимое копий НЕ ПРОВЕРЕНЫ.'),
)
BY_SECTION = {r.section: r for r in RULES}
