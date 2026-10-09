# План развития и критерии приёмки

| Этап | Результат | Критерий |
|---|---|---|
| MVP 0.1.0a1 | локальный CLI, 12 правил, строгая схема, JSON/Markdown, fixtures | опубликован, 18 продуктовых тестов, packages/assets/SHA256 проверены |
| 0.1.0a2 | русская документация/UI, полный индекс, MIT, security/license материалы, согласованная версия | отдельный PR/зелёный CI, 31 тест, включая регрессии лицензии, fresh install/uninstall/license inclusion, новый immutable tag и проверенный prerelease |
| Проектирование live collector | точные endpoints/permissions/licenses/scope/auth | reviewed матрица, отдельный test tenant, доказуемый read-only transport; ещё НЕ ВЫПОЛНЕНО |
| Реальный сбор/нормализация | guarded Graph/ARM adapters, provenance и полнота страниц | реальные минимальные grants, 401/403/429/nextLink/partial tests; не выдавать ошибки за pass |
| Полнота правил | группы/custom roles, effective CA/OIDC/network | отдельные положительные/отрицательные lab cases и документированные ограничения |
| Эксплуатационная приёмка | доставка журналов, backup status и отдельный restore | owner-approved evidence, cleanup, приватное хранение и независимый review |

Текущий продукт не управляет инфраструктурой и не реализует HTTP API. Нет обещаний сроков, автоматического provisioning, production запуска или стабильного выпуска. Разрешение разработки/PR/release не разрешает создавать платные ресурсы или входить в реальные tenants.

Для новых правил нужны точная применимость, все необходимые поля, severity rationale, evidence/remediation/limitations и good/bad/unknown/not_run cases. Breaking schema/report изменения требуют явной версии и миграционной инструкции. Новый collector нельзя «включить» только потому, что SDK установился.

Операционные gates: [LOCAL-PC.md](LOCAL-PC.md), [SECURITY-TESTING.md](SECURITY-TESTING.md), [RELEASE-CHECKLIST.md](RELEASE-CHECKLIST.md). Сохранённый первоначальный план: [docs/07-mvp-plan.md](docs/07-mvp-plan.md).
