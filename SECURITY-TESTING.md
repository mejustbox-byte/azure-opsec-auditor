# Проверки безопасности и непроверенные gates

Тесты работают на синтетических данных и локальных Git/артефактных моделях; они не подтверждают настройки Azure tenant. Полный запуск — `python -m unittest discover -s tests -v`. Источник тестов: [tests/test_auditor.py](tests/test_auditor.py), [tests/test_release_control.py](tests/test_release_control.py).

| Контроль | Содержательная проверка | Предел |
|---|---|---|
| Схема | Лишние поля, типы bool/int, bounds, duplicate keys/ids, NaN, UTC | Не подтверждает правдивость источника |
| Входной файл | Ограниченный размер; FIFO в subprocess с timeout; отказ non-regular и закрытие fd | Медленный regular file на сетевом FS всё ещё может задержать чтение |
| Правила | Все 12 good/bad; unknown/not_run/mixed; свежесть и приоритет exit code | Узкие predicates, не effective access |
| Вывод | Не выводить invalid payload; Ограничения строк/enum и Markdown на валидированном вводе; русская справка/схема | Нет универсальной редакции чувствительных id |
| Пакеты | Реальная установка wheel/sdist вне checkout, CLI/JSON/Markdown, uninstall | Локально Linux; Windows НЕ ВЫПОЛНЕНО |
| Лицензия | MIT metadata и идентичные LICENSE/русское пояснение в обоих архивах | Не независимое юридическое заключение |
| Release | Версия/tag/commit, inventory, SHA mismatch, отказ чужих/лишних assets, повторная публикация | Тесты mock не заменяют реальный Actions release |
| Публичный git | Сигнатурный скан без печати совпадений, ссылки и индекс документов | Не полный secret/DLP scanner |

Фактически выполненные команды, CI и выпуск фиксируются в [VERIFICATION.md](VERIFICATION.md), а не выводятся из таблицы. Скрипт проверки артефактов дополнительно проверяет архивы перед публикацией; live gates в [LOCAL-PC.md](LOCAL-PC.md).


При изменении parser/renderer добавлять регрессию против конкретного риска. FIFO тест должен завершаться timeout-контролируемо, а не зависать весь runner. CI fail не обходить отключением tests/hashes. Новый collector потребует отдельного threat review, read-only scope/pagination/rate-limit tests и проверки credential isolation до появления live заявлений.
