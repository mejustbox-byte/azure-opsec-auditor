# Выпуск и целостность артефактов

Текущая версия пакета `0.1.0a2` соответствует **только** tag `v0.1.0a2`. Старый `v0.1.0a1` сохраняется. До реального Azure lab выпуск остаётся prerelease. PyPI не используется. Инструкции требуют уже разрешённых пользователем GitHub операций и фактически зелёного CI, не подразумевают право создания облачных ресурсов.

## Подготовка

1. Обновить версии, русские документы, CHANGELOG/notes, lock и схемы согласованно; выполнить [VERIFICATION.md](VERIFICATION.md) и [RELEASE-CHECKLIST.md](RELEASE-CHECKLIST.md).
2. Создать PR, проверить CI именно финального HEAD, затем слить. Проверить main CI и получить полный `git rev-parse HEAD` после синхронизации. Исторические CI результаты не заменяют новый запуск.
3. Убедиться, что tag ещё не существует локально/удалённо; создать annotated tag на проверенном commit. Нельзя force push, передвигать или удалять существующий tag. Создать draft prerelease с русскими notes и target равным полному SHA, без upload локальных assets.

Пример после подстановки действительного SHA:

```bash
git tag -a v0.1.0a2 FULL_MAIN_SHA -m 'Предварительный выпуск 0.1.0a2'
git push origin refs/tags/v0.1.0a2
gh release create v0.1.0a2 --verify-tag --target FULL_MAIN_SHA --draft --prerelease --title 'Azure / Entra: локальный аудитор 0.1.0a2' --notes-file RELEASE-NOTES.md
gh workflow run release.yml --ref main -f tag=v0.1.0a2 -f expected_commit=FULL_MAIN_SHA
```

`FULL_MAIN_SHA` — placeholder, не буквальный аргумент. При необходимости использовать штатный git credential helper подключённого `gh`, не извлекать credentials. Редактирование видимых notes старого выпуска допустимо; старые архивы не пересобирать.

## Штатный Actions workflow

[release.yml](.github/workflows/release.yml) запускается вручную из main. Автоматизация и release-source checkout разделены; action SHA закреплены. Workflow сверяет формат tag/SHA, существующий tag, HEAD, ancestry main, чистые tracked файлы и package version. Затем устанавливает hashed build tools, выполняет тесты/скан, собирает и проверяет wheel/sdist, нормализует timestamps контейнеров, создаёт примеры/документацию/manifest.

Только release job получает `contents:write`, token доступен финальному publish step. [publish_release.py](scripts/publish_release.py) проверяет удалённый tag и соответствующий draft prerelease, загружает отсутствующие assets без clobber, скачивает и сравнивает все пять файлов, затем публикует и повторяет проверку. Отличающиеся/лишние assets, чужой target, не-prerelease и неверный tag вызывают отказ. Повторный запуск уже опубликованного идентичного выпуска только проверяет его. Никаких новых credentials и обхода auth.

## Проверка после публикации

В `gh release view` проверить `isDraft=false`, `isPrerelease=true`, tag и target; фактический peeled tag должен совпадать с утверждённым commit. Inventory: wheel, sdist, examples.zip, documentation.zip, SHA256SUMS. Скачать в пустой отдельный каталог:

```bash
gh release download v0.1.0a2 --dir /tmp/opsec-published-a2
cd /tmp/opsec-published-a2
sha256sum -c SHA256SUMS
```

Manifest покрывает четыре артефакта. Проверить MIT metadata и оба license files; выполнить чистую установку wheel и sdist вне checkout, CLI fixtures и удаление. Не считать mock tests доказательством реальной публикации. Обновить русские release notes фактическими ссылками CI/release job/commit и непроверенными lab gates. Сохранить русские инструкции среды и финальный HEAD в draft; публикация среды и восстановление — отдельно.

При неуспехе workflow оставить draft и существующий tag, описать конкретный блокер; не публиковать вручную непроверенные файлы. Rollback пользователя — установка предыдущей версии в отдельный venv, а не переписывание tag. Сохранённая подробная процедура: [docs/08-release.md](docs/08-release.md).
