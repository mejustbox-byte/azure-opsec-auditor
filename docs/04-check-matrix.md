# Матрица реализованных правил v1

Правила проверены на синтетических нормализованных метаданных. Реальные Azure/Entra: **НЕ ПРОВЕРЕНО**. Все перечисленные поля обязательны для результата; отсутствие/null даёт `unknown`. Пороги — явно выбранные базовые значения MVP, а не утверждение о соответствии Microsoft. Severity описывает потенциальный риск правила и сохраняется также при pass/unknown.

| Правило / раздел | Нормализованные поля | Условие fail | Ограничение |
|---|---|---|---|
| RBAC-01 / rbac | privileged, assignment, scope_level | privileged + permanent + subscription/management_group/directory | нет раскрытия групп, наследования, custom roles |
| PIM-01 / pim | plane, approval_required, mfa_required, max_activation_hours | нет approval/MFA либо длительность вне 1–8 часов | только конфигурация; обе planes обозначены, но не собираются |
| CA-01 / conditional_access | state, privileged_target_included, privileged_target_excluded | не enabled, target не включён или исключён | одна target-policy запись, не общий охват |
| MFA-01 / mfa | privileged_target, strength, enforced | privileged target без enforced phishing_resistant strength | регистрация/сессии не проверяются |
| SP-01 / service_principals | privileged, owner_count, credential_expired | privileged и нет владельцев либо credential истёк | нет activity или credential values |
| OAUTH-01 / oauth | grant_type, permissions | application grant содержит Directory.ReadWrite.All, RoleManagement.ReadWrite.Directory, AppRoleAssignment.ReadWrite.All, Application.ReadWrite.All или Mail.ReadWrite | ограниченный список; delegated grants и другие permissions не оцениваются этим условием |
| OIDC-01 / identities | kind, broad_privilege, issuer_trusted, subject_exact, audience_expected | broad privilege либо federated identity без любого trust flag | флаги утверждает normalizer; managed identity игнорирует federation flags |
| KV-01 / key_vault | public_network_access, default_action, soft_delete, purge_protection | public+allow либо отсутствует защита удаления | нет effective RBAC, trusted services или secret-content |
| ST-01 / storage | allow_blob_public_access, container_access | account разрешает anonymous и container имеет blob/container access | account flag отдельно недостаточен; нет anonymous request |
| NET-01 / network | direction, action, any_source, ports | inbound+allow+any source и 0(все),22,3389,1433,3306 или 5432 | нет приоритетов, диапазонов, ASG, маршрутов или сканирования |
| LOG-01 / logging | enabled, destination_configured, retention_days | выключено, нет destination либо retention <30 дней | доставка и охват tenant не проверены |
| REC-01 / recovery | policy_configured, last_backup | нет policy либо last status не success | нет времени backup job, содержания или restore |

Точные enum/types/ranges описаны в `schemas/snapshot-v1.json`. `fixtures/{good,bad,unknown,not_run,mixed}.json` покрывают статусы; тесты дополнительно проверяют границы, каждое отсутствующее поле, stale/partial/unavailable и некорректный ввод.
