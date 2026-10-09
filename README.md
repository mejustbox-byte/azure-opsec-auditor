# azure-opsec-auditor

Аудитор состояния безопасности Azure / Entra: анализирует **нормализованные локальные метаданные только чтением**, без подключения к облаку. Предварительная версия пакета `0.1.0a2`, тег выпуска `v0.1.0a2`. Проверки охватывают RBAC/PIM, Conditional Access, фишинг-устойчивую MFA, service principals, OAuth, managed/federated identities, Key Vault, анонимный доступ к Storage, сетевые правила, журналирование и метаданные резервного копирования.

**Реальные Azure/Entra API, разрешения, доставка журналов и восстановление НЕ ПРОВЕРЕНЫ.** Разработка и проверки используют синтетические данные. `pass` относится к конкретной записи и узкому правилу, а не подтверждает безопасность tenant целиком. Нет облачной аутентификации, сетевого сбора, создания ресурсов или автоматического исправления.

## Установка и запуск

Требуется Python 3.12+. Из [предварительного выпуска](https://github.com/mejustbox-byte/azure-opsec-auditor/releases/tag/v0.1.0a2) скачайте `azure_opsec_auditor-0.1.0a2-py3-none-any.whl` и `SHA256SUMS`, проверьте указанный SHA256 файла, затем выполните:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --no-index --no-deps ./azure_opsec_auditor-0.1.0a2-py3-none-any.whl
.venv/bin/azure-opsec-auditor --version
```

В Windows используйте `.venv\Scripts\python.exe` и `.venv\Scripts\azure-opsec-auditor.exe`. Публикация в PyPI не выполняется. Из checkout можно запускать без установки:

```sh
python3 -m azure_opsec_auditor fixtures/good.json --as-of 2026-10-09T12:00:00Z
python3 -m azure_opsec_auditor fixtures/bad.json --as-of 2026-10-09T12:00:00Z --format markdown
```

Первый пример возвращает код 0; второй — 1. `fixtures/unknown.json`, `not_run.json` и `mixed.json` возвращают 2. Исторический `--as-of` нужен для воспроизводимого примера, а не для подтверждения актуальности устаревших реальных данных. Для текущих снимков опускайте этот аргумент; допустимый возраст по умолчанию 7 дней (`--max-age-days` от 1 до 365). Если перенаправляете stdout в файл, используйте защищённое локальное хранилище и не публикуйте реальные отчёты.

`examples.zip` содержит синтетические снимки и схему. После распаковки запускайте те же примеры установленной командой `azure-opsec-auditor`. Вход должен соответствовать [схеме снимка](schemas/snapshot-v1.json); сырые экспорты tenant не поддерживаются. Неизвестные поля и некорректный ввод отвергаются без вывода переданных значений. Неполные источники и отсутствующие поля дают `unknown`/`not_run`, а не ложный `pass`.

## Разработка и проверка

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --require-hashes --only-binary=:all: -r requirements-build.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/check_repository.py
.venv/bin/python -m build --no-isolation
.venv/bin/python scripts/verify_distribution.py
```

Сторонних зависимостей времени выполнения нет. Версии инструментов сборки закреплены, хеши проверяются. CI выполняет тесты, сборку и проверку пакетов на Linux с Python 3.12/3.13 без облачных credentials. В управляемой среде достаточно `bash scripts/install.sh`: команда работает без сохранённого venv. См. [процедуру выпуска](docs/08-release.md) и [настройку среды](docs/09-environment.md).

## Полный индекс документации

- [Шаблон сообщения об ошибке](.github/ISSUE_TEMPLATE/bug_report.md)
- [Шаблон PR](.github/PULL_REQUEST_TEMPLATE.md)
- [Инструкции для последующих циклов разработки](AGENTS.md)
- [Архитектура локального аудитора](ARCHITECTURE.md)
- [История изменений](CHANGELOG.md)
- [Облачная разработка и восстановление среды](CLOUD-DEVELOPMENT.md)
- [Вклад в проект](CONTRIBUTING.md)
- [Контракт CLI, JSON и Python library](CORE-CONTRACT.md)
- [Evidence, отчёты и хранение](EVIDENCE.md)
- [Установка, проверка и удаление](INSTALL.md)
- [Лицензия MIT: пояснение и справочный перевод](LICENSE.ru.md)
- [Локальная лаборатория Azure / Entra](LOCAL-PC.md)
- [Контроль выпуска 0.1.0a2](RELEASE-CHECKLIST.md)
- [v0.1.0a2 — локальный аудитор Azure / Entra 0.1.0a2](RELEASE-NOTES.md)
- [Выпуск и целостность артефактов](RELEASE.md)
- [Примечания к выпуску](RELEASE_NOTES.md)
- [План развития и критерии приёмки](ROADMAP.md)
- [Эксплуатация локального аудитора](RUNBOOK.md)
- [Проверки безопасности и непроверенные gates](SECURITY-TESTING.md)
- [Политика безопасности](SECURITY.md)
- [Зависимости, лицензии и целостность выпуска](SUPPLY-CHAIN.md)
- [Стек и закреплённые версии](TECH-STACK.md)
- [Границы доверия и модель угроз](THREAT-MODEL.md)
- [Протокол проверок](VERIFICATION.md)
- [Требования GITHUB-OPSEC / Azure и Entra](docs/01-requirements.md)
- [Модель угроз](docs/02-threat-model.md)
- [Архитектура](docs/03-architecture.md)
- [Матрица реализованных правил v1](docs/04-check-matrix.md)
- [Проверки, CI и реальная лаборатория](docs/05-lab-and-ci.md)
- [ADR-001: Python MVP с локальным анализом](docs/06-adr-stack.md)
- [План MVP и условия выпуска](docs/07-mvp-plan.md)
- [Процедура выпуска](docs/08-release.md)
- [Управляемая среда разработки](docs/09-environment.md)
- [Полнота документации и сопоставление](docs/10-documentation-coverage.md)
- [Стандартный текст лицензии MIT](LICENSE)
- [Машиночитаемая схема снимка](schemas/snapshot-v1.json)

Не добавляйте реальные секреты, экспорты tenant, UPN или чувствительные отчёты в публичный git. Храните реальные снимки вне checkout либо в отдельном защищённом каталоге; `.gitignore` не является границей безопасности. Разработка и CI не используют реальные Azure credentials или платные ресурсы. Старый выпуск `0.1.0a1` сохраняется с неизменным тегом и артефактами; перевод распространяется новым выпуском.
