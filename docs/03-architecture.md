# Архитектура

Реализованный путь: `CLI → bounded UTF-8 JSON loader → schema validator → pure rules → JSON/Markdown stdout`. Нет сети, auth, фоновых сервисов или Azure SDK. Каталог определяет поля, severity, условие риска, remediation и ограничения. `schema.py` генерирует JSON Schema и валидирует поддерживаемое подмножество стандартной библиотекой.

## Входной контракт

Корень: `schema_version:1`, `synthetic:boolean`, псевдоним `scope`, UTC `collected_at`, `sections`. Именованный раздел: `status` (complete/partial/unavailable/not_run), `source`, `api_version`, `records`. Запись содержит уникальный `id` внутри раздела и поля матрицы. `null` или отсутствующее поле означает недоступное evidence; `id` обязателен. Неизвестные поля запрещены. unavailable/not_run не могут содержать записи. Пустой complete даёт `unknown`, а не подтверждение безопасного охвата.

Одна дата снимка применяется ко всем записям: нельзя объединять старые данные под новой датой. Укажите самое раннее время сбора либо разделите снимки. Неблокирующее открытие и `fstat` отвергают FIFO/devices/directories до bounded read; fd всегда закрывается. JSON Schema описывает структуру; runtime дополнительно проверяет уникальность id, календарные UTC-даты, дубликаты JSON-ключей и возраст.

## Результаты и охват

По одному finding на запись; дополнительный finding по охвату для partial/empty. Отсутствующий источник даёт `not_run`; устаревший доступный — `unknown` без оценки записей. Если обязательное поле отсутствует/null, запись даёт `unknown`, даже если другое поле выглядит рискованным: консервативное правило MVP может скрыть известный риск при неполной нормализации. Полные записи оцениваются в стабильном порядке правил/id.

Результат содержит версии источника/API/правила, evidence, confidence, severity, причину, ограничения и ручную remediation. Evidence — предоставленные нормализованные данные, не сырой API-ответ. Русские описания не меняют ключи JSON, enum и идентификаторы правил.

Код 2 при unknown/not_run или ошибке ввода; иначе 1 при fail, иначе 0. `--as-of` фиксирует историческое время; по умолчанию используется текущий UTC. Допустимый возраст 7 дней, настраивается в пределах 1–365; будущая дата запрещена. CLI не пишет выходные файлы: перенаправлением и permissions управляет оператор.

## Будущий облачный сбор — не реализован

Graph: directory roles/PIM, CA/auth strengths, service principals, grants, federation и registration reports. ARM: RBAC/PIM, resources, identities, vaults, storage, NSGs, diagnostics и backup metadata. Auth adapter и transport проектируются отдельно от правил. Нельзя незаметно переключать tenant через default credential chain. Точные endpoint permissions и licenses проверяются в отдельном tenant; ARM Reader или один Graph grant не считаются универсальным доступом. listKeys/secret-content APIs исключены.
