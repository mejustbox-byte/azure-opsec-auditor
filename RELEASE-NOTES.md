# v0.1.0a2 — локальный аудитор Azure / Entra 0.1.0a2

Предварительный выпуск переводит документацию, справку CLI, пользовательские сообщения, описания правил и схемы на русский. Добавлены полный индекс и самостоятельные документы архитектуры, стека, установки, контрактов, эксплуатации, лаборатории, проверок и выпуска. Расширены модель угроз, хранение evidence, цепочка поставки и security testing; добавлены русский AGENTS.md, стандартный MIT LICENSE и русское пояснение, MIT metadata и проверка включения обоих файлов в wheel/sdist. Команды, пути, JSON-ключи, идентификаторы и логика 12 правил сохранены. Python-пакет `0.1.0a2` соответствует тегу `v0.1.0a2`; старый `v0.1.0a1` и assets не изменяются.

Аудитор анализирует только локальные нормализованные метаданные: evidence/severity/remediation, pass/fail/unknown/not_run, JSON/Markdown и охват. Нет runtime dependencies, сетевого сбора, cloud auth или auto-remediation. Не использовались реальные Azure credentials и платные ресурсы.

## Установка и примеры

Требуется Python 3.12+. Скачайте wheel и SHA256SUMS, проверьте указанный хеш файла:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --no-index --no-deps ./azure_opsec_auditor-0.1.0a2-py3-none-any.whl
.venv/bin/azure-opsec-auditor --version
```

Распакуйте examples.zip и выполните из его каталога:

```sh
/path/to/.venv/bin/azure-opsec-auditor fixtures/good.json --as-of 2026-10-09T12:00:00Z
/path/to/.venv/bin/azure-opsec-auditor fixtures/bad.json --as-of 2026-10-09T12:00:00Z --format markdown
```

Коды: good=0, bad=1, unknown/not_run/mixed=2. Историческое время — только для примеров; текущие данные должны укладываться в допустимый возраст. В Windows используйте `.venv\Scripts\`. Публикация в PyPI не выполняется.

## Проверки

Unit/CLI/release-control tests покрывают 12 правил, границы, некорректный parser/schema ввод, FIFO/nonblocking/закрытие fd, свежесть и неполные источники, tag/version mapping, повреждение assets, отказ upload без публикации и воспроизводимость контейнеров. Установка wheel/sdist проверяется вне source tree; подписи секретов и локальные ссылки сканируются; build tools проверяются по hashes. Локально прошли 31 тест, свежая установка без сохранённого venv, скан ссылок/сигнатур/индекса, сборка, установка и удаление wheel/sdist вне checkout. В обоих пакетах проверены MIT metadata и точные тексты LICENSE/LICENSE.ru.md. Четыре локальных SHA256 совпали. Удалённые [PR CI](https://github.com/mejustbox-byte/azure-opsec-auditor/actions/runs/37929097228) и [push CI](https://github.com/mejustbox-byte/azure-opsec-auditor/actions/runs/37929092499) на commit `3b41058a80486834d8b1d6fedb54e6910af12fd0` успешны на Python 3.12/3.13: 31 тест, сборка, license inclusion и изолированная установка/удаление. Изменения проходят через [PR #3](https://github.com/mejustbox-byte/azure-opsec-auditor/pull/3). Полный source SHA и финальные ссылки main/release добавляются в видимые notes после их проверки.

Assets: wheel, sdist, examples.zip, documentation.zip, SHA256SUMS. Схема и ограничения включены в документацию. Release workflow использует штатный `GITHUB_TOKEN`, проверяет tag/commit и скачанные assets/SHA256 до и после публикации без переписывания tags/assets.

**НЕ ПРОВЕРЕНО:** реальные Azure/Entra API/auth, endpoint permissions/licenses, сбор/pagination, effective RBAC/groups/CA, OIDC semantics, сетевая достижимость, доставка журналов, backup restore и cleanup. Live collector не реализован. Синтетические тесты не проверяют реальную инфраструктуру; нужна отдельно разрешённая disposable лаборатория и проверенная нормализация. `pass` относится только к переданной записи и узкому условию, а не всему tenant. Реальные exports, secrets и reports нельзя помещать в публичный git/артефакты.
