# Зависимости, лицензии и целостность выпуска

У проекта нет runtime-зависимостей и Azure SDK. Собственный пакет распространяется по MIT: [LICENSE](LICENSE), справочное русское пояснение [LICENSE.ru.md](LICENSE.ru.md). Оба файла включаются в wheel и sdist; verifier сравнивает их с исходниками и проверяет `License-Expression: MIT` в metadata. Лицензия не является гарантией безопасности.

## Инвентарь

| Компонент | Точная версия / фиксация | Роль | Лицензия |
|---|---|---|---|
| Python | >=3.12; локально 3.12.14, CI 3.12/3.13 | Интерпретатор/stdlib | PSF и включённые upstream notices |
| setuptools | 80.9.0 | Backend сборки | MIT |
| wheel | 0.45.1 | Сборка wheel | MIT |
| build | 1.3.0 | Frontend сборки | MIT |
| packaging | 25.0 | Служебные зависимости сборки | Apache-2.0 / BSD по включённым upstream текстам |
| pyproject-hooks | 1.2.0 | Протокол backend | MIT |
| actions/checkout | 34e114876b0b11c390a56381ad16ebd13914f8d5 (v4.3.1) | Checkout CI | MIT upstream |
| actions/setup-python | a26af69be951a213d495a4c3e4e4022e16d87065 (v5.6.0) | Python CI | MIT upstream |

Python patch в Actions и bundled pip создаваемого venv не закреплены этим lock; это ограничение воспроизводимости, не полный hermetic build. `requirements-build.txt` закрепляет пять инструментов wheel hashes; metadata официальных wheel проверены, но автоматический SBOM/CVE monitor и независимый license audit **НЕ ВЫПОЛНЕНО**. Источники: [PyPI](https://pypi.org/), [checkout](https://github.com/actions/checkout), [setup-python](https://github.com/actions/setup-python). Транзитивные build-зависимости перечислены в lock; дополнительные зависимости не должны устанавливаться неявно.

## Контроли

Установка с `--require-hashes --only-binary=:all:` и сборка `--no-isolation`; wheel/sdist устанавливаются с `--no-index --no-deps --no-build-isolation` после подготовки backend. TLS/hashes не отключать. Изменения lock/version/actions требуют review официального источника, сравнения лицензий и повторной установки/тестов. GitHub token не сохраняется в checkout; release job имеет `contents:write`, обычный CI — `contents:read`.

Workflow сверяет tag, полный commit, ancestry main и package version; публикация использует существующий draft prerelease, отказывается передвигать tag, перезаписывать отличающиеся assets или публиковать чужой commit. Артефакты проверяются после скачивания до и после публикации. Контрольные суммы `SHA256SUMS` покрывают wheel, sdist, examples.zip и documentation.zip. Сам manifest сравнивается с локально построенным при release.

SHA256 подтверждает совпадение байтов с manifest, но не удостоверяет автора, если manifest получен через тот же скомпрометированный канал. Sigstore, attestations и независимые воспроизводимые сборки **НЕ ВЫПОЛНЕНО**. Источник доверия — проверенный GitHub repository/tag/workflow и TLS. Нормализация timestamps контейнеров не означает побитовую независимую reproducibility между разными Python/tools.

## Содержимое

Архивы содержат только исходники/документацию/синтетические fixtures, не credentials и не реальные evidence. Signature scan не доказывает отсутствие всех секретов; ручное ревью остаётся обязательным. Перед выпуском проверить полный inventory, license inclusion и чистую установку по [RELEASE-CHECKLIST.md](RELEASE-CHECKLIST.md); поддержка уязвимостей — [SECURITY.md](SECURITY.md).
