# План MVP и условия выпуска

Реализованы локальный CLI, versioned normalized schema, 12 узких правил, evidence/severity/remediation, pass/fail/unknown/not_run, воспроизводимые JSON/Markdown, синтетические fixtures, unit/CLI integration tests, hashed build tools, CI, wheel/sdist проверки. Версия `0.1.0a2` переводит документацию и пользовательские описания, сохраняя семантику правил.

Условия выпуска: тесты, сигнатурный скан и diff/архивное ревью; соответствие схемы; сборка wheel/sdist и установка вне source; SHA256; отдельная feature branch/PR; фактический зелёный CI; слияние через PR; новый тег на точном финальном main. Для `0.1.0a2` тег — `v0.1.0a2`. Старый `v0.1.0a1` и assets не передвигаются/не удаляются. Actions workflow публикует существующий matching prerelease draft и проверяет tag/assets/SHA256 до и после публикации. Недоступная операция фиксируется как блокер, а не успех.

Дальше: endpoint/permission/license matrix, scope/auth adapters, защищённые read-only Graph/ARM collectors, provenance/pagination completeness, полнота групп/ролей/CA, OAuth resolution, provider-specific OIDC и effective network. Live tests только opt-in и отдельно разрешённые. Этот выпуск не является аттестацией production tenant.
