# Полнота документации и сопоставление

Структурная база сравнения — набор документов sigma-ruleforge, autonomous-pentest-ai, modular-c2-framework, redblue-arena и honeypot-grid, проверенный управляющим чатом. Дополнительно прочитаны публичные main документы honeypot-grid INSTALL/RUNBOOK/CLOUD-DEVELOPMENT/LOCAL-PC/RELEASE-CHECKLIST и redblue-arena VERIFICATION/MODULE-API. Их функции, стек и результаты не перенесены: этот проект — Python offline CLI, без HTTP API, контейнерных служб и live collector.

| Смысловой раздел прежних проектов | Самостоятельный документ этого MVP |
|---|---|
| Назначение/границы/полный индекс | [README](../README.md), [требования](01-requirements.md) |
| Архитектура/стек/обоснование | [ARCHITECTURE](../ARCHITECTURE.md), [TECH-STACK](../TECH-STACK.md), [ADR](06-adr-stack.md) |
| Установка/проверка/удаление | [INSTALL](../INSTALL.md) |
| Разработка/review/этапы/приёмка | [CONTRIBUTING](../CONTRIBUTING.md), [ROADMAP](../ROADMAP.md), [план](07-mvp-plan.md) |
| Угрозы/security/trust/retention | [THREAT-MODEL](../THREAT-MODEL.md), [SECURITY](../SECURITY.md), [EVIDENCE](../EVIDENCE.md), [SECURITY-TESTING](../SECURITY-TESTING.md) |
| API/CORE-CONTRACT/MODULE-API | [CORE-CONTRACT](../CORE-CONTRACT.md): только фактические CLI/JSON/library контракты и расширение правил |
| RUNBOOK/OPERATIONS | [RUNBOOK](../RUNBOOK.md): private reports, ошибки, обновление/rollback |
| Cloud development/restore | [CLOUD-DEVELOPMENT](../CLOUD-DEVELOPMENT.md) |
| Local PC/infra/lab | [LOCAL-PC](../LOCAL-PC.md): synthetic vs отдельный Azure tenant |
| Verification/release | [VERIFICATION](../VERIFICATION.md), [RELEASE](../RELEASE.md), [RELEASE-CHECKLIST](../RELEASE-CHECKLIST.md), [RELEASE-NOTES](../RELEASE-NOTES.md) |
| Supply-chain/license/history | [SUPPLY-CHAIN](../SUPPLY-CHAIN.md), [LICENSE](../LICENSE), [русское пояснение](../LICENSE.ru.md), [CHANGELOG](../CHANGELOG.md) |
| Последующие циклы | [AGENTS](../AGENTS.md) |

Старые docs/01–09 сохранены и связаны с корневыми документами: требования, predicates, схема, ADR и лаборатория уточняют корневой обзор. Проверка полноты основана на наличии конкретных контрактов, команд, рисков и gates, а не числе страниц. README индекс и локальные ссылки проверяются скриптом. Неисполненные реальные gates перечислены явно, чужие результаты CI не выдаются за результаты этого проекта.
