# Протокол проверок

## Команды текущего цикла

Все данные синтетические. Для повторения из checkout с Python 3.12+:

```bash
OPSEC_VENV_DIR=/tmp/opsec-fresh-env bash scripts/install.sh
/tmp/opsec-fresh-env/bin/python -m unittest discover -s tests -v
/tmp/opsec-fresh-env/bin/python scripts/check_repository.py
/tmp/opsec-fresh-env/bin/python -m build --no-isolation
/tmp/opsec-fresh-env/bin/python scripts/verify_distribution.py
/tmp/opsec-fresh-env/bin/python scripts/release_assets.py
cd dist
sha256sum -c SHA256SUMS
```

Installer проверяет dependencies/test/scan/good CLI. Distribution verifier создаёт независимые venv вне checkout, устанавливает каждый архив без runtime downloads, проверяет пять fixture exit codes/JSON и Markdown, удаляет пакет и проверяет отсутствие импорта. Проверяет `License-Expression: MIT`, LICENSE/LICENSE.ru.md и их точные байты. Release assets сканируются по сигнатурам; отсутствие совпадений не доказывает отсутствие любых секретов.

## Исторические факты

- PR [#1](https://github.com/mejustbox-byte/azure-opsec-auditor/pull/1): offline MVP; merge commit `698372c2b6f54707561da22e3f9ac52668c2e4a5`; [main CI](https://github.com/mejustbox-byte/azure-opsec-auditor/actions/runs/37924158317), 18 тестов на Python 3.12/3.13.
- PR [#2](https://github.com/mejustbox-byte/azure-opsec-auditor/pull/2): Actions release control; merge `c037cebb8bb468aa2c6d8801ba95c1226f601ec6`; [main CI](https://github.com/mejustbox-byte/azure-opsec-auditor/actions/runs/37925422932), 25 тестов.
- [Первый prerelease](https://github.com/mejustbox-byte/azure-opsec-auditor/releases/tag/v0.1.0a1) сохранён на первом commit; [release job](https://github.com/mejustbox-byte/azure-opsec-auditor/actions/runs/37925426045) успешен, пять assets скачаны, четыре SHA256 проверены. Видимые название/описание переведены без изменения tag/commit/архивов.

## Текущий 0.1.0a2

Локально выполнена установка в новом `/tmp/opsec-fresh-a2` без сохранённого venv, 31 тест успешно (без пропусков на Linux), скан ссылок/сигнатур/полного индекса — без ошибок. Собраны wheel/sdist; оба прошли проверку MIT metadata/лицензий, изолированную установку, CLI и удаление. Созданы пять assets, четыре SHA256 совпали. Удалённый CI и выпуск фиксируются ниже после фактического выполнения; локальные проверки их не заменяют. Для публикации использовать только финальный main и новый tag `v0.1.0a2`, не перемещать старый.

## НЕ ВЫПОЛНЕНО

Реальная Azure/Entra лаборатория, лицензии/API permissions, effective RBAC/groups/CA/MFA, OIDC, delegated OAuth, эффективные сети, доставка журналов/retention и восстановление; см. [LOCAL-PC.md](LOCAL-PC.md). Windows execution и ACL, восстановление среды в новой cloud задаче, внешнее security review, независимый rebuild, SBOM/CVE monitor, подписи/attestations также не выполнены. Проверки в mock release tests отличать от реально выполненного GitHub Actions release.
