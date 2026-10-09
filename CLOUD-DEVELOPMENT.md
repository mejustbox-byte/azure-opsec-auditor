# Облачная разработка и восстановление среды

Среда предназначена для локального offline MVP, тестов и сборки Python-пакетов. Azure tenant, службы, контейнеры и платные ресурсы для разработки не нужны. Текущий checkout: `/workspace/azure-opsec-auditor`; использовать его, не создавать Git worktree без отдельного запроса.

## Воспроизводимая установка

Нужны Git, Bash, Python 3.12+ с venv/pip и доступ к источнику зависимостей. Скрипт не полагается на сохранённый venv:

```bash
cd /workspace/azure-opsec-auditor
OPSEC_VENV_DIR=/tmp/opsec-fresh-env bash scripts/install.sh
/tmp/opsec-fresh-env/bin/python -m unittest discover -s tests -v
/tmp/opsec-fresh-env/bin/python scripts/check_repository.py
/tmp/opsec-fresh-env/bin/azure-opsec-auditor fixtures/good.json --as-of 2026-10-09T12:00:00Z
```

Скрипт устанавливает инструменты с `--require-hashes`, пакет из checkout без runtime-зависимостей, проверяет `pip check`, тесты, ссылки/сигнатуры и CLI. При повторном запуске актуализирует тот же venv; отдельный `/tmp` venv доказывает независимость от сохранённой `.venv`. Для сборки выполнять команды из [VERIFICATION.md](VERIFICATION.md).

## Настройки среды

Полный `install_script` для draft:

```bash
#!/usr/bin/env bash
set -euo pipefail
cd /workspace/azure-opsec-auditor
bash scripts/install.sh
```

`start_skill` должен по-русски предписывать проверить checkout/AGENTS.md и текущую версию, выполнить установку при отсутствии venv, запустить тесты, скан и good fixture, затем при работе над выпуском собрать и проверить wheel/sdist. Долгоживущие процессы запускать не нужно. Не сохранять credentials, реальные snapshot или результаты tenant в инструкции.

Сетевые package-manager presets сохраняются. `api.github.com` и `uploads.github.com` допустимы для штатных GitHub операций; наличие домена не создаёт авторизацию. Использовать существующее подключение/официальный GitHub credential helper, не извлекать token. Если локальный upload недоступен, [release workflow](.github/workflows/release.yml) использует штатный job-scoped GITHUB_TOKEN, без новых секретов.

Сохранённый draft — только конфигурация для ревью. Пользователь должен сохранить настройки и опубликовать среду. Восстановление опубликованного snapshot в новом cloud task — отдельная проверка, **НЕ ВЫПОЛНЕНО** в текущем цикле. Нельзя объявлять её успешной по факту сохранения draft.

## Публикация и восстановление

В draft записывать полный фактический HEAD checkout и правильный mount_path, а не предполагаемый remote tip. Перед публикацией убедиться, что изменения доступны в GitHub, в индекс не попали отчёты/данные, установка воспроизводится. После восстановления в новой задаче проверить `pwd`, `git rev-parse HEAD`, наличие файлов, Python, выполнить `scripts/install.sh`, все проверки и фиксированный good fixture. Если snapshot содержит старую версию, безопасно обновить согласованный checkout; не передвигать release tags.

Потерянный venv восстанавливается скриптом. Исходники восстанавливаются из соответствующего неизменяемого tag; приватные отчёты имеют отдельную политику резервирования и не входят в среду проекта. Блокеры установки, CI, auth и сохранения draft фиксировать раздельно; инструкции не заменяют фактически выполненные команды.

См. [INSTALL.md](INSTALL.md), [RELEASE.md](RELEASE.md), [EVIDENCE.md](EVIDENCE.md) и сохранённую [docs/09-environment.md](docs/09-environment.md).
