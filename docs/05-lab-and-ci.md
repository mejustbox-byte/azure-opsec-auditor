# Проверки, CI и реальная лаборатория

## Локальные проверки

Python 3.12+: `python -m unittest discover -s tests -v`, `python scripts/check_repository.py`, сборка с hashed requirements через `python -m build --no-isolation`. `scripts/verify_distribution.py` устанавливает wheel и sdist во временные venv и запускает установленный CLI вне source tree. Нет runtime dependencies или Azure credentials. Fixtures представляют нормализованные данные, а не настоящие ответы Graph/ARM.

`.github/workflows/ci.yml`: push/pull_request, Linux Python 3.12/3.13, pinned checkout/setup-python, `contents:read`, timeout, hashed build tools, тесты, скан и проверки пакетов. Проверенные официальные tags: `actions/checkout` v4.3.1 → `34e114876b0b11c390a56381ad16ebd13914f8d5`; `actions/setup-python` v5.6.0 → `a26af69be951a213d495a4c3e4e4022e16d87065`. Проверка выполнена read-only `git ls-remote` в официальных repo.

Нет Azure login, PR secrets, live jobs или tenant artifacts. Наличие workflow не доказывает успешный удалённый запуск: фактические ссылки фиксируются отдельно в release notes. Branch protection настраивает владелец; автоматически она не меняется. Release control отдельно проверяет immutable tag, существующие assets и SHA256; эти тесты не являются tenant-проверками.

## Реальная лаборатория — НЕ ПРОВЕРЕНО

В этой версии нет live collector. CLI не подключается к Azure. Нужен отдельно разрешённый disposable test tenant/subscription, владелец, согласованные бюджет, licenses и cleanup plan. Эта задача не создаёт ресурсов и не использует реальные Azure credentials.

1. Владелец фиксирует tenant/subscription allowlists и scope, защищает от CA lockout проверенным emergency access. По актуальной Microsoft документации определяет точные stable Graph/ARM permissions и Entra/PIM licensing. Аудитору не назначают write grants.
2. Отдельный операторский инструмент создаёт безопасные test identities/roles/policies и пустые vault/storage/network resources, logging/backup примеры. Никаких production данных; нельзя публиковать populated storage или чувствительные сервисы. Provisioning не входит в аудитор.
3. Независимо проверенная read-only процедура сбора/нормализации фиксирует endpoint/API, source status, самое раннее время, pagination completeness и отсутствующие grants. Поля матрицы сопоставляются явно: privilege, effective CA assertions, OAuth names и OIDC flags CLI не вычисляет. Псевдонимы и `synthetic:false`; сырые exports/reports не коммитятся.
4. Сравните findings с ожидаемой конфигурацией. Отдельно проверьте группы/наследование/custom roles, обе PIM planes, CA exclusions/strengths, OAuth resolution, provider-specific OIDC, effective vault/storage/network access и доставку telemetry. Недоступные API/licenses дают `unknown`; отсутствующие значения не выдумываются.
5. Restore — отдельно разрешённое упражнение владельца с отдельными permissions и безопасными backup data. Успешные метаданные не являются evidence восстановления. Результаты/cleanup фиксируются отдельно.
6. Evidence хранится защищённо вне git с TTL/access policy. Ресурсы удаляет владелец. Невыполненные сбор, доставка, restore или cleanup отмечаются НЕ ПРОВЕРЕНО.

Остаются непроверенными: auth/API, permissions/licenses, live collector/pagination, effective policy/network, доставка журналов, restore и cleanup. Предварительный выпуск явно сообщает эти ограничения.
