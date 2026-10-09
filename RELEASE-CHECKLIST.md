# Контроль выпуска 0.1.0a2

Чеклист — условия приёмки, а не автоматическое заявление об успехе. Фактический протокол: [VERIFICATION.md](VERIFICATION.md); notes: [RELEASE-NOTES.md](RELEASE-NOTES.md).

| Gate | Требуемое доказательство |
|---|---|
| Источник | Проверенный PR/финальный HEAD, main CI зелёный, clean tracked files |
| Версия | pyproject/__version__ 0.1.0a2; новый tag v0.1.0a2 на полном final main SHA |
| Старый выпуск | v0.1.0a1, исходный commit и архивы не изменены |
| Документы | Русские самостоятельные документы, полный README index, локальные ссылки, правильные команды/ограничения |
| Безопасность | Threat/evidence/supply-chain/testing документы; нет реальных credentials/exports/отчётов; сигнатурный скан без раскрытия значений |
| Лицензия | Стандартный MIT LICENSE, русское пояснение; MIT metadata/оба файла в wheel/sdist |
| Тесты | Реальный unit/integration запуск, FIFO subprocess timeout, все 12 правил, unknown/not_run |
| Установка | Свежий venv из checkout, hashed lock, wheel/sdist изолированно, CLI и uninstall |
| Actions | Штатный release workflow на утверждённом tag/SHA; scoped contents:write/GITHUB_TOKEN |
| Assets | Пять точных имён; downloaded SHA256SUMS четыре OK; опубликованное состояние prerelease, не draft |
| Среда | Русские install_script/start_skill и точный checkout HEAD сохранены в draft |

Обязательные ограничения в notes: Azure/Entra live gates, Windows, новая cloud задача/restore, независимый security audit/attestation **НЕ ВЫПОЛНЕНО**. Эти gates не заменять synthetic pass; именно поэтому prerelease. Нельзя заявлять платную лабораторию созданной или обещать работающий private disclosure канал, которого нет.
