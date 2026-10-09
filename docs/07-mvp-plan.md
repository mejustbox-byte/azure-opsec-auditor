# MVP plan and release gates

Delivered scope: offline CLI, versioned normalized schema, twelve narrow rules, evidence/severity/remediation, pass/fail/unknown/not_run, deterministic JSON/Markdown, synthetic fixtures, unit/CLI integration tests, hashed build tooling and CI workflow, wheel/sdist smoke checks.

Release gates: tests pass; repository signature scan and diff/artifact review; schema synchronization; build wheel/sdist; install each outside source tree; verify CLI and synthetic expected status; produce SHA256 manifest; commit/push feature branch; create PR; inspect remote CI; merge through PR only after successful available checks; tag merged commit; publish prerelease with assets and limitations. If GitHub API/network/authorization or required remote CI is unavailable, preserve the branch/artifacts and report the exact blocked gates without claiming PR, merge or release success.

Backlog after lab validation: endpoint/permission/license matrix; explicit scope/auth adapters; guarded read-only Graph/ARM collectors; normalization with provenance and pagination completeness; full coverage/group/role semantics; OAuth permission resolution; provider-specific OIDC and effective network analysis. Keep live tests opt-in and separately authorized. This release is not a production-tenant security attestation.
