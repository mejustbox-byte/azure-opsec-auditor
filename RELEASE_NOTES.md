# v0.1.0a1 — offline Azure / Entra posture MVP (prerelease)

First usable offline CLI: versioned normalized JSON input, strict validation, twelve narrow metadata rules, evidence/severity/remediation, pass/fail/unknown/not_run, JSON/Markdown reports and coverage. There are no runtime dependencies, network calls, cloud authentication or remediation. No paid resources or real credentials were used.

Install with Python 3.12+ after downloading the wheel and SHA256SUMS and verifying its listed hash:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --no-index --no-deps ./azure_opsec_auditor-0.1.0a1-py3-none-any.whl
.venv/bin/azure-opsec-auditor --version
```

Extract examples.zip, then from its directory:

```sh
/path/to/.venv/bin/azure-opsec-auditor fixtures/good.json --as-of 2026-10-09T12:00:00Z
/path/to/.venv/bin/azure-opsec-auditor fixtures/bad.json --as-of 2026-10-09T12:00:00Z --format markdown
```

Expected exits: good=0, bad=1, unknown/not_run/mixed=2. Historical replay is for examples; current data must meet the freshness budget. Windows uses `.venv\Scripts\` executables.

Local validation: unit and CLI integration suite with all twelve rules, negative parsing/schema cases, freshness/boundary/partial-source coverage; wheel and sdist installed and exercised outside source tree; repository and release archive signature scan; hash-locked build tools. Remote CI outcome must be verified before publishing; do not infer it from workflow presence.

Assets: wheel, sdist, examples.zip, documentation.zip, SHA256SUMS. This is not a PyPI release. Schema and exact rule limitations are included in the documentation.

**NOT VERIFIED:** live Azure/Entra API behavior, authentication, endpoint permission/licensing matrix, real collection/pagination, effective RBAC/groups/CA coverage, OIDC provider semantics, network reachability, diagnostic delivery, backup restore and lab cleanup. No live collector is implemented. Synthetic tests do not validate real infrastructure; a separate authorized disposable lab and reviewed normalization procedure are required. A pass describes only a supplied record and narrow predicate, not tenant-wide safety. Keep real exports, secrets and reports out of public git/artifacts.
