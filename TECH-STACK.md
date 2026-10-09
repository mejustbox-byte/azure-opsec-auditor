# Стек и закреплённые версии

Выбран Python со стандартной библиотекой: малый проверяемый парсер, чистые правила, unittest, JSON/Markdown. Нет Azure SDK, HTTP-клиента, web framework, Docker или базы. Нулевые runtime dependencies снижают поверхность поставки; достоверность метаданных всё равно зависит от оператора. Обоснование/альтернативы — [ADR](docs/06-adr-stack.md).

| Компонент | Фактическая версия/закрепление | Роль |
|---|---|---|
| Python | requires >=3.12; в Cloud проверен 3.12.14; CI матрица 3.12/3.13 | выполнение и стандартная библиотека |
| setuptools | 80.9.0 | backend и MIT package metadata |
| wheel | 0.45.1 | сборка wheel |
| build | 1.3.0 | frontend wheel/sdist |
| packaging | 25.0 | зависимость сборки |
| pyproject-hooks | 1.2.0 | вызов build backend |
| actions/checkout | v4.3.1, 34e114876b0b11c390a56381ad16ebd13914f8d5 | получение проверенного кода |
| actions/setup-python | v5.6.0, a26af69be951a213d495a4c3e4e4022e16d87065 | Python runner |

`requirements-build.txt` закрепляет все пять build tools точными версиями и SHA256 официальных универсальных wheels; установка требует `--require-hashes --only-binary=:all:`. `pyproject.toml` повторно фиксирует setuptools backend. Отдельного runtime lock не нужно: dependencies пусты. Ветки Actions не используются вместо commit pins. Python patch для CI не закреплён: задаётся minor 3.12/3.13; поэтому не заявляется побайтовая идентичность всей ОС/toolchain.

Тесты — стандартный unittest; отдельные pytest/Ruff/uv не установлены и не заявляются проверенными. Подписи секретов и ссылки проверяет scripts/check_repository.py. Схема генерируется из каталога, а её артефакт сверяется тестом; добавление нового schema keyword требует реализации в валидаторе.

Пакет `0.1.0a2` / тег `v0.1.0a2`, MIT. Лицензии и происхождение инструментов: [SUPPLY-CHAIN.md](SUPPLY-CHAIN.md). Обновление tools/pins требует отдельного изменения lock, проверки официального происхождения, пересборки и CI; не подменяйте hashes и не отключайте TLS.
