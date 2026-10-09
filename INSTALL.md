# Установка, проверка и удаление

Продукт требует Python >=3.12. Подтверждённый профиль — Linux/POSIX, Cloud Python 3.12.14 и CI Python 3.12/3.13. Wheel платформенно нейтрален, но реальный Windows-запуск **НЕ ВЫПОЛНЕН**; команды Windows ниже являются инструкцией для отдельной проверки. Нужны только локальные файлы; Azure CLI/login, tenant credentials и Docker не нужны.

## Проверка скачанных assets

Из [выпуска v0.1.0a2](https://github.com/mejustbox-byte/azure-opsec-auditor/releases/tag/v0.1.0a2) скачайте wheel, sdist, examples.zip, documentation.zip и SHA256SUMS в один каталог. На Linux:

```sh
sha256sum -c SHA256SUMS
```

Все четыре перечисленных файла должны дать OK. Если скачан только wheel, сравните его SHA256 с соответствующей строкой manifest. В PowerShell используйте `Get-FileHash -Algorithm SHA256 .\azure_opsec_auditor-0.1.0a2-py3-none-any.whl` и сравните с manifest. Хеш не доказывает личность издателя; сверяйте release/tag/commit и источник manifest.

## Wheel: POSIX

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --no-index --no-deps ./azure_opsec_auditor-0.1.0a2-py3-none-any.whl
.venv/bin/python -m pip check
.venv/bin/azure-opsec-auditor --version
.venv/bin/azure-opsec-auditor --help
```

Ожидается `0.1.0a2` и русская справка. Распакуйте examples.zip и из каталога с fixtures выполните команду установленного CLI по абсолютному пути:

```sh
/path/to/.venv/bin/azure-opsec-auditor fixtures/good.json --as-of 2026-10-09T12:00:00Z
/path/to/.venv/bin/azure-opsec-auditor fixtures/bad.json --as-of 2026-10-09T12:00:00Z --format markdown
```

Коды 0/1 соответственно; unknown/not_run/mixed дают 2. Историческая дата используется только для примеров. Не публикуйте реальные отчёты.

## Wheel: Windows / PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --no-index --no-deps .\azure_opsec_auditor-0.1.0a2-py3-none-any.whl
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\azure-opsec-auditor.exe --version
.\.venv\Scripts\python.exe -X utf8 -m azure_opsec_auditor --help
.\.venv\Scripts\python.exe -X utf8 -m azure_opsec_auditor fixtures\good.json --as-of 2026-10-09T12:00:00Z
```

`-X utf8` задаёт UTF-8 для перенаправленной русской справки/отчёта. При ошибке не объявляйте поддержку подтверждённой: сохраните только синтетическое воспроизведение, фактический Python/exit и передайте issue без чувствительных данных. Для проверенного профиля используйте Linux.

## Исходники и разработка

```sh
git clone https://github.com/mejustbox-byte/azure-opsec-auditor.git
cd azure-opsec-auditor
git checkout --detach v0.1.0a2
bash scripts/install.sh
.venv/bin/python -m build --no-isolation
.venv/bin/python scripts/verify_distribution.py
.venv/bin/python scripts/release_assets.py
```

Существующий checkout сначала проверьте `git status --short`/HEAD; не удаляйте чужие изменения через reset/clean. Для разработки создайте ветку от проверенного main; detached tag нужен для точного воспроизведения выпуска. scripts/install.sh создаёт venv, ставит hashed tools/local editable package и выполняет проверки.

Из sdist распакуйте исходники и выполните тот же setup. Для установки sdist в уже подготовленный venv: `python -m pip install --no-index --no-deps --no-build-isolation ./azure_opsec_auditor-0.1.0a2.tar.gz`. Нужен setuptools 80.9.0 из проверенного build lock; путь requirements-build.txt есть в распакованных исходниках. Публикация в PyPI не выполнена.

## Удаление и обновление

```sh
.venv/bin/python -m pip uninstall --yes azure-opsec-auditor
.venv/bin/python -I -c "import importlib.util; assert importlib.util.find_spec('azure_opsec_auditor') is None"
```

В Windows используйте соответствующий Scripts\python.exe. Удаление пакета не удаляет снимки, stdout-отчёты, резервные копии или checkout. Удалять собственный venv можно только после проверки пути; приватные данные удаляются отдельно по retention. Проверка установки/удаления обоих пакетов выполняется scripts/verify_distribution.py во временных venv.

Обновляйте отдельный venv из проверенного нового wheel; сначала hashes/версия/синтетические примеры. Старые tags/assets не меняйте. Ограничения и работа с реальными данными: [RUNBOOK.md](RUNBOOK.md), [EVIDENCE.md](EVIDENCE.md).
