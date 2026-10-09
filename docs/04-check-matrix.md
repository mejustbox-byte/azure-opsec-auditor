# Implemented rule matrix v1

All rules are tested on synthetic normalized metadata. Azure/Entra live behavior: **NOT VERIFIED**. Each listed field is required for a verdict; absent/null gives unknown. All thresholds are documented MVP baselines, not claims of Microsoft compliance. Severity describes the risk when present; a pass/unknown finding retains the rule's potential severity.

| Rule / section | Normalized fields | Fail predicate | Limitation |
|---|---|---|---|
| RBAC-01 / rbac | privileged, assignment, scope_level | privileged + permanent + subscription/management_group/directory | no inheritance/group/custom-role expansion |
| PIM-01 / pim | plane, approval_required, mfa_required, max_activation_hours | no approval/MFA or duration outside 1–8 hours | configuration only, both planes labeled but not collected |
| CA-01 / conditional_access | state, privileged_target_included, privileged_target_excluded | not enabled, not included, or excluded | one target-policy assertion, not aggregate coverage |
| MFA-01 / mfa | privileged_target, strength, enforced | privileged target without enforced phishing_resistant strength | no registration/session verification |
| SP-01 / service_principals | privileged, owner_count, credential_expired | privileged and no owners or expired credential | no activity or credential values |
| OAUTH-01 / oauth | grant_type, permissions | application grant includes Directory.ReadWrite.All, RoleManagement.ReadWrite.Directory, AppRoleAssignment.ReadWrite.All, Application.ReadWrite.All or Mail.ReadWrite | limited list; delegated grants and other permissions not assessed for risk by this predicate |
| OIDC-01 / identities | kind, broad_privilege, issuer_trusted, subject_exact, audience_expected | broad privilege; or federated identity lacks any trust flag | flags asserted by normalizer; managed identities ignore federation flags |
| KV-01 / key_vault | public_network_access, default_action, soft_delete, purge_protection | public+allow or either deletion safeguard off | no effective RBAC, trusted-service or secret-content checks |
| ST-01 / storage | allow_blob_public_access, container_access | account permits anonymous access and container is blob/container | account flag alone not a failure; no anonymous request |
| NET-01 / network | direction, action, any_source, ports | inbound+allow+any source and 0(all),22,3389,1433,3306 or 5432 | no effective priorities, ranges, ASGs, routing or scans |
| LOG-01 / logging | enabled, destination_configured, retention_days | disabled, no destination or retention <30 days | delivery/tenant-wide coverage unverified |
| REC-01 / recovery | policy_configured, last_backup | no policy or last status not success | no job timestamp, content or restore verification |

`schemas/snapshot-v1.json` contains exact enum/type/range constraints. `fixtures/{good,bad,unknown,not_run,mixed}.json` cover the status contract; tests additionally exercise boundary conditions, every missing rule field, stale/partial/unavailable evidence and invalid input.
