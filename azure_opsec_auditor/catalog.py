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
    Rule('RBAC-01', 'rbac', 'Permanent broad privileged assignment', 'high',
         {'privileged': BOOL, 'assignment': enum('permanent', 'eligible', 'active'),
          'scope_level': enum('resource', 'resource_group', 'subscription', 'management_group', 'directory')},
         lambda x: x['privileged'] and x['assignment'] == 'permanent' and x['scope_level'] in ('subscription', 'management_group', 'directory'),
         'Review broad privilege; reduce scope and use time-bound eligibility where appropriate.',
         'Evaluates normalized privilege/scope only; does not expand groups, inheritance or custom role actions.'),
    Rule('PIM-01', 'pim', 'Privileged activation safeguards', 'high',
         {'plane': enum('entra', 'azure'), 'approval_required': BOOL, 'mfa_required': BOOL,
          'max_activation_hours': {'type': 'integer', 'minimum': 0, 'maximum': 8760}},
         lambda x: not x['approval_required'] or not x['mfa_required'] or not 0 < x['max_activation_hours'] <= 8,
         'Review activation policy: require approval, MFA and a positive duration of at most eight hours.',
         'Eight hours is a baseline, not a Microsoft guarantee; eligibility and actual activation are not collected.'),
    Rule('CA-01', 'conditional_access', 'Privileged target CA coverage assertion', 'high',
         {'state': enum('enabled', 'report_only', 'disabled'), 'privileged_target_included': BOOL, 'privileged_target_excluded': BOOL},
         lambda x: x['state'] != 'enabled' or not x['privileged_target_included'] or x['privileged_target_excluded'],
         'Review effective policies for the target, exclusions and emergency access before enforcing coverage.',
         'One normalized target-policy record; does not calculate effective policy coverage or model sign-in conditions.'),
    Rule('MFA-01', 'mfa', 'Phishing-resistant requirement for a privileged target', 'high',
         {'privileged_target': BOOL, 'strength': enum('phishing_resistant', 'mfa', 'single_factor'), 'enforced': BOOL},
         lambda x: x['privileged_target'] and (x['strength'] != 'phishing_resistant' or not x['enforced']),
         'Require an appropriate phishing-resistant authentication strength on privileged access; validate exclusions.',
         'Configuration assertion only; registered methods and actual session enforcement remain unverified.'),
    Rule('SP-01', 'service_principals', 'Orphaned or stale privileged principal', 'high',
         {'privileged': BOOL, 'owner_count': COUNT, 'credential_expired': BOOL},
         lambda x: x['privileged'] and (x['owner_count'] == 0 or x['credential_expired']),
         'Assign accountable owners, review privilege and retire expired credentials without exporting their values.',
         'Owner/expiry metadata only; no credential contents, activity or reachability assessment.'),
    Rule('OAUTH-01', 'oauth', 'High-impact application permission grant', 'high',
         {'grant_type': enum('application', 'delegated'), 'permissions': {'type': 'array', 'items': {'type': 'string', 'pattern': '^[A-Za-z][A-Za-z0-9._-]{0,127}$'}, 'maxItems': 50, 'uniqueItems': True}},
         lambda x: x['grant_type'] == 'application' and bool(set(x['permissions']) & {'Directory.ReadWrite.All', 'RoleManagement.ReadWrite.Directory', 'AppRoleAssignment.ReadWrite.All', 'Application.ReadWrite.All', 'Mail.ReadWrite'}),
         'Review admin consent and remove unnecessary high-impact application permissions using a separate approved change.',
         'Small explicit high-impact list, not comprehensive. Resolved permission names are input assertions; usage is not checked.'),
    Rule('OIDC-01', 'identities', 'Managed/federated identity privilege and trust', 'high',
         {'kind': enum('managed', 'federated'), 'broad_privilege': BOOL, 'issuer_trusted': BOOL,
          'subject_exact': BOOL, 'audience_expected': BOOL},
         lambda x: x['broad_privilege'] or (x['kind'] == 'federated' and not (x['issuer_trusted'] and x['subject_exact'] and x['audience_expected'])),
         'Reduce identity privilege and bind federation to reviewed issuer, exact subject and expected audience.',
         'Trust is normalized by the operator; no issuer lookup or provider-specific matching. Managed identities ignore federation flags.'),
    Rule('KV-01', 'key_vault', 'Vault exposure and deletion safeguards', 'high',
         {'public_network_access': BOOL, 'default_action': enum('allow', 'deny'), 'soft_delete': BOOL, 'purge_protection': BOOL},
         lambda x: (x['public_network_access'] and x['default_action'] == 'allow') or not x['soft_delete'] or not x['purge_protection'],
         'Review vault network restrictions, enable soft delete and purge protection through an approved change.',
         'Management configuration only; does not read secrets or verify effective RBAC, trusted services or DNS.'),
    Rule('ST-01', 'storage', 'Anonymous container exposure', 'high',
         {'allow_blob_public_access': BOOL, 'container_access': enum('private', 'blob', 'container')},
         lambda x: x['allow_blob_public_access'] and x['container_access'] != 'private',
         'Disable unnecessary anonymous blob access and set containers private after reviewing application requirements.',
         'Configured anonymous access only; no blob download or verification of network reachability.'),
    Rule('NET-01', 'network', 'Unrestricted sensitive inbound rule', 'high',
         {'direction': enum('inbound', 'outbound'), 'action': enum('allow', 'deny'), 'any_source': BOOL,
          'ports': {'type': 'array', 'items': {'type': 'integer', 'minimum': 0, 'maximum': 65535}, 'maxItems': 50, 'uniqueItems': True}},
         lambda x: x['direction'] == 'inbound' and x['action'] == 'allow' and x['any_source'] and bool(set(x['ports']) & {0, 22, 3389, 1433, 3306, 5432}),
         'Restrict sources and sensitive inbound ports; validate effective NSG priority and network topology separately.',
         'Port 0 denotes all ports in this schema. No priority, ranges, ASG, route or active reachability analysis.'),
    Rule('LOG-01', 'logging', 'Diagnostic configuration and retention', 'medium',
         {'enabled': BOOL, 'destination_configured': BOOL, 'retention_days': {'type': 'integer', 'minimum': 0, 'maximum': 36500}},
         lambda x: not x['enabled'] or not x['destination_configured'] or x['retention_days'] < 30,
         'Configure required diagnostics and a destination retaining at least 30 days, or document an approved baseline.',
         'Thirty days is an MVP baseline. Configuration does not prove delivery or tenant-wide coverage.'),
    Rule('REC-01', 'recovery', 'Backup configuration and last status', 'high',
         {'policy_configured': BOOL, 'last_backup': enum('success', 'failed', 'never')},
         lambda x: not x['policy_configured'] or x['last_backup'] != 'success',
         'Review backup coverage and failed jobs; conduct an independently authorized restore drill.',
         'Last status has no freshness assertion beyond snapshot age; restore and backup contents are NOT VERIFIED.'),
)
BY_SECTION = {r.section: r for r in RULES}
