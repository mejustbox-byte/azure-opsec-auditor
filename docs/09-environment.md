# Управляемая среда разработки

Продукт и все необходимые документы находятся в `/workspace/azure-opsec-auditor`. Каталог onboarding и сохранённый venv не требуются. Используйте существующий изолированный checkout; Git worktree создавайте только по явному запросу. Не нужны сервисы, Docker, Azure CLI, облачный login или credentials.

## Установка и обновление

Из checkout выполните `bash scripts/install.sh`. Скрипт проверяет Python >=3.12, создаёт `.venv`, устанавливает build tools с точными hashes и локальный editable package без build isolation/runtime dependency resolution, проверяет pip, запускает unit/CLI/release-control tests и repository scan, затем установленный CLI на синтетическом good fixture.

Для независимой проверки создайте новый временный каталог и выполните `OPSEC_VENV_DIR=/absolute/new/path bash scripts/install.sh`; прежний venv не используйте. Управляемая среда проверяется на Linux/bash. Ручная установка описана в README; управляемый Windows setup не проверен.

## Начало задачи

Выполните `.venv/bin/azure-opsec-auditor --version`; при отсутствии команды запустите установку. Из checkout: `.venv/bin/python -m unittest discover -s tests -v`, `.venv/bin/python scripts/check_repository.py`. Пример `fixtures/good.json --as-of 2026-10-09T12:00:00Z` возвращает 0; bad=1, unknown/not_run/mixed=2. Постоянные процессы не нужны.

## Сборка и готовность

`.venv/bin/python -m build --no-isolation`, `.venv/bin/python scripts/verify_distribution.py`, `.venv/bin/python scripts/release_assets.py`. Сигнатурный/ссылочный скан и изолированные package checks — локальные evidence, а не удалённый CI или Azure validation. Реальные credentials, exports и reports запрещены в публичном git/артефактах.

`install_script`: `set -euo pipefail`, `cd /workspace/azure-opsec-auditor`, `bash scripts/install.sh`. Русский `start_skill` содержит команды выше и фактическое описание продукта. В конфигурации сохраняется точный проверенный commit checkout. Сохранение draft не применяет изменения, не публикует среду и не доказывает восстановление в новой задаче. После review/save/publish настроек выполните startup checks в новой задаче.

GitHub API/upload domains могут быть разрешены для авторизованных операций; credential values не сохраняются. Git push и API/upload имеют разный доступ. Штатный `git -c credential.helper='!gh auth git-credential' push` использует предоставленную auth без вывода значений. При upload 401 применяется проверенный Actions workflow со штатным `GITHUB_TOKEN`, а не обход auth. Новые credentials не добавляются. Русские notes и version/tag должны соответствовать фактическому выпуску; `0.1.0a2` → `v0.1.0a2`.
