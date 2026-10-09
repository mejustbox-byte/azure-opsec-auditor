# Процедура выпуска

Python-пакет `0.1.0a2`, Git/тег `v0.1.0a2`; предварительный выпуск, поскольку реальные платформенные проверки не выполнены. PyPI и production readiness не заявляются. Старый `v0.1.0a1` и его артефакты сохраняются.

Из чистого checkout выполните команды разработки из README. `python scripts/release_assets.py` создаёт `examples.zip` (синтетические snapshots/schema), `documentation.zip` (русские README/security/contributing/changelog/docs) и `SHA256SUMS` рядом с wheel/sdist в `dist/`. Всего пять assets; GitHub также предоставляет source archives. SHA256 подтверждает согласованность, но не личность издателя; получайте manifest из того же проверенного выпуска.

Изменения вносите отдельным PR, проверьте удалённый CI и слейте проверенный HEAD. Соберите из финального main; создайте новый тег ровно на этом commit. Не передвигайте уже существующие tags и не перезаписывайте assets. В русских notes укажите точные local/remote результаты, installation/run и реально невыполненные Azure/Entra/restore проверки. Проверьте tag, опубликованный prerelease и скачанные assets; локальная сборка не равна публикации.

## Штатный выпуск через Actions

При недоступной авторизации uploads.github.com в cloud CLI используйте `.github/workflows/release.yml` в проверенном main со штатным `GITHUB_TOKEN` job. Новых секретов или credential bindings не нужно. Сам workflow должен быть слит отдельным PR после зелёного CI.

Ручной dispatch получает существующий alpha tag и полный разрешённый commit SHA. Поддерживается формат `v0.1.0a2` → `0.1.0a2`; legacy `v0.1.0a1` → `0.1.0a1` сохраняется. Проверки отвергают branch names, malformed refs, несовпадение версии, изменённый tag и commit вне main ancestry. Checkout pins официальные; credentials не сохраняются. `contents:write` есть только у release job, `GH_TOKEN` доступен только финальному шагу upload/publish. Workflow не создаёт, не reset и не push tags.

Workflow собирает и тестирует точный tag, нормализует только metadata контейнеров wheel/sdist для воспроизводимых повторов, проверяет установку, создаёт синтетические/документальные assets и SHA256. Нужен существующий prerelease draft с совпадающим target. Существующие assets сравниваются, не clobber; несовпадающие данные или stable release прерывают работу. До публикации скачиваются/проверяются все пять assets; после проверяются state/tag/inventory и они скачиваются/проверяются снова. Повтор для опубликованного совпадающего выпуска только читает данные.

После создания тега и draft на проверенном main:

```sh
gh workflow run release.yml --repo mejustbox-byte/azure-opsec-auditor --ref main -f tag=v0.1.0a2 -f expected_commit=FULL_MERGE_SHA
```

Замените `FULL_MERGE_SHA` точным SHA финального main. Наблюдайте реальный run, а не предполагайте успех по наличию workflow. Реальная лаборатория и незавершённые платформенные проверки: [инструкция](05-lab-and-ci.md).
