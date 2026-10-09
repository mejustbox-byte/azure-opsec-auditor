# ADR-001: offline-first Python MVP

Accepted 2026-10-09 for offline MVP only. Python >=3.12, standard-library CLI/schema validator/rule engine/unittest, normalized JSON and JSON/Markdown reports. No cloud SDK, custom OAuth, auth adapter or live transport in the release. The offline binary boundary has no credential or network requirement.

Alternatives considered: PowerShell Graph/Az is convenient for administration but less suitable for a small isolated parser/rule artifact; TypeScript adds a second package/tooling ecosystem; Go single-binary distribution is useful but increases initial rule/schema iteration cost. Python favors readable rules and cheap offline tests; runtime installation remains required.

Build-only tools are exact-version hash-locked in requirements-build.txt. Runtime dependency list is empty. JSON Schema is generated from the catalog and committed; the runtime validator supports only the constructs generated here plus semantic checks. Tests enforce artifact/catalog synchronization. Adding a new schema keyword requires extending the validator and tests, or adopting a maintained validator in a separate ADR with a hashed lock.

This avoids installing a cloud SDK before permissions/API design is validated. Future auth should use a maintained Microsoft library; do not implement OAuth manually. Future SDK vs explicit REST must be decided against method/host/tenant/pagination guards and API drift. Reviewed dependencies and endpoint-specific permission checks are prerequisites, not already completed work.

Rejected for this MVP: asserting tenant-wide safety from record predicates, auto-remediation, credential acquisition and unverified live collectors. Review this ADR when runtime support, schema complexity, throughput or collection requirements change.
