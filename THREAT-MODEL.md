# Границы доверия и модель угроз

Защищаем локальные evidence/отчёты, целостность публичного кода/пакетов, runtime credentials и доверие оператора к результатам. Угрозы: ложный/злонамеренный снимок, недоверенный PR, скомпрометированный инструмент сборки/runner, ошибочная нормализация или хранение. Оператор и ОС доверены; CLI не предоставляет многопользовательский sandbox.

Границы: оператор/файл → JSON parser → schema → pure rules → stdout/хранилище оператора. Отдельно: PR → CI → reviewed main/tag → release job → public assets. В MVP нет границы OAuth/Graph/ARM: облачный сбор не реализован.

| Сценарий | Контроль | Проверка | Остаточный риск |
|---|---|---|---|
| JSON ambiguity/инъекция | duplicate-key rejection, известные поля, строгие типы/ASCII identifiers | malformed/duplicate/type tests | допустимые ложные значения остаются возможны |
| FIFO/размер/глубина → DoS | O_NONBLOCK, fstat regular file, 5 MiB, bounded lists/strings и RecursionError | subprocess timeout, закрытие fd, limits | медленный regular-file storage или stdout может блокировать |
| Неполнота → ложный pass | unknown/not_run/coverage, возраст, консервативные missing fields | partial/unavailable/stale/missing | complete утверждает оператор; scope не проверяется живым сбором |
| Отчёт раскрывает метаданные | псевдонимы, приватный каталог, retention вне git | no-echo error и scan | допустимые identifiers/evidence намеренно выводятся, полной анонимизации нет |
| Credential/cloud mutation | нет auth/network/SDK в продукте | socket-denial test | инструменты оператора вне границы CLI |
| PR крадёт runtime token | CI read-only, без secrets; release только main, token только final step | workflow/release-control review и CI | доверенный runner/owner может быть скомпрометирован |
| Подмена source/tag/assets | reviewed HEAD, exact SHA/tag/version, hashes, no clobber, download before/after | tag mismatch/tampering/failure/retry tests | SHA256 не удостоверяет издателя, GitHub/owner доверены |
| Зависимость/лицензия потеряна | нулевые runtime deps, hashed tools, pins, MIT files/metadata | package scan и inclusion | нужен review каждого будущего обновления |

Будущий live transport обязан проверять tenant/audience/host/verb/redirect/nextLink, limits/retries и минимальные grants. Эти требования НЕ ВЫПОЛНЕНЫ и не заявляются как текущие гарантии. Реальная CA/identity/network/restore оценка требует [LOCAL-PC.md](LOCAL-PC.md).

Контроли хранения: [EVIDENCE.md](EVIDENCE.md); лицензии/целостность: [SUPPLY-CHAIN.md](SUPPLY-CHAIN.md); сообщения об уязвимости: [SECURITY.md](SECURITY.md). Сохранённая исходная модель: [docs/02-threat-model.md](docs/02-threat-model.md).
