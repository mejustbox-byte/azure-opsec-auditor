# Контракт CLI, JSON и Python library

Контракт относится к локальному пакету `0.1.0a2`. HTTP API, сервер, внешняя загрузка plugins и облачная auth отсутствуют. Все входные данные — local normalized JSON; команды/keys/enum остаются неизменными при русских описаниях.

## CLI

`azure-opsec-auditor snapshot [--format {json,markdown}] [--as-of UTC] [--max-age-days N]`, также `--help`/`--version`. snapshot — regular UTF-8 файл до 5 MiB. FIFO/devices/directories отвергаются неблокирующим open + fstat. Возраст 1–365 дней, по умолчанию 7. UTC строго YYYY-MM-DDTHH:MM:SSZ, календарно валидный, без будущей даты относительно оценки.

stdout: один JSON-report или Markdown; stderr: безопасная ошибка без значений JSON/неизвестных ключей. При невалидном вводе stdout пуст. Аргументы оболочки могут попасть в сообщения argparse; не передавайте secrets как параметры. Ввод неизменен, файлов отчёта CLI не создаёт. Коды 0 (полные данные, нет fail), 1 (полные данные, fail), 2 (ошибка/unknown/not_run), 2 имеет приоритет.

## Вход v1

Корневые поля: schema_version=1, synthetic boolean, scope, collected_at, sections. scope/source/api_version/id — ограниченные ASCII псевдонимы до 128 символов. Каждый раздел status=complete/partial/unavailable/not_run, source, api_version, records<=1000; unavailable/not_run требуют пустого списка. id уникален внутри раздела. Допустимые sections и fields заданы в [схеме](schemas/snapshot-v1.json) и [матрице](docs/04-check-matrix.md); списки ограничены 50, bool не принимается вместо int, NaN/Infinity и duplicate JSON keys запрещены.

Поля правила могут быть отсутствующими/null: это unknown, не ошибка структуры. Unknown property, неверный enum/type/range — ошибка. Runtime дополнительно проверяет unique id, calendar validity/freshness; JSON Schema не заменяет эти проверки. synthetic=false разрешает будущий операторский снимок, но не доказывает live validation или безопасную публикацию.

## Report v1

Поля: report_version, tool_version, mode=offline, synthetic, scope, as_of, max_age_days, platform_validation, summary, exit_code, coverage, findings. summary считает pass/fail/unknown/not_run; число findings может превышать число записей из-за coverage finding.

Finding: rule_id, rule_version, title, resource_ref, status, severity, confidence, evidence, source, api_version, collected_at, reason, remediation, limitations. Severity high/medium — потенциальный риск правила; confidence normalized_metadata/insufficient_evidence, а не оценка достоверности tenant. Evidence содержит словарь предоставленных полей правила и их значений; это не JSON paths и не сырой API ответ. Русские title/reason/remediation/limitations не являются стабильными identifiers; автоматизация использует rule_id/status/versions.

## Library

```python
from azure_opsec_auditor.schema import load, validate, InputError
from azure_opsec_auditor.engine import audit, markdown

snapshot = load("fixtures/good.json")
report = audit(snapshot, as_of="2026-10-09T12:00:00Z", max_age_days=7)
assert report["exit_code"] == 0
text = markdown(report)
```

load(path) читает/валидирует файл; validate(dict) проверяет структуру и возвращает ту же ссылку; audit(dict, *, as_of=None, max_age_days=7) валидирует, не меняет input и возвращает dict; markdown(report) предназначен для report, созданного audit, не для произвольного недоверенного dict. InputError — ValueError с безопасным сообщением; caller отвечает за обработку ошибок и приватный stdout. Вызовы не делают сеть/auth.

## Расширение правил

Добавьте reviewed Rule в catalog.RULES и описания новых fields в schema.DESCRIPTIONS. Зарегистрируйте id/section в коде; не импортируйте Python paths из JSON. Predicate работает только с валидированными complete fields и не делает side effects. Сгенерируйте snapshot-v1.json, добавьте good/bad/unknown/not_run/границы, сравните старые результаты. Новое правило может изменить coverage/exit для старых снимков: отсутствие нового section даст not_run; breaking контракт требует явной миграции/версии. Подробности — [CONTRIBUTING.md](CONTRIBUTING.md).
