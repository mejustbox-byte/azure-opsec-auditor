# azure-opsec-auditor

Offline, read-only Azure / Entra posture auditing of **normalized metadata**, not a live Azure collector. Alpha `0.1.0a1` checks RBAC/PIM, Conditional Access, phishing-resistant MFA, service principals, OAuth grants, managed/federated identities, Key Vault, anonymous Storage/network exposure, logging and backup metadata.

**Azure/Entra platform behavior, live permissions, logging delivery and restore are NOT VERIFIED.** Only synthetic development data has been exercised. A pass applies to the supplied record and narrow rule, never to the whole tenant. No cloud authentication, network requests, resource creation or remediation.

## Install and run

Requires Python 3.12+. Download `azure_opsec_auditor-0.1.0a1-py3-none-any.whl` and `SHA256SUMS` from the prerelease assets, verify the SHA256 listed for that asset, then:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --no-index --no-deps ./azure_opsec_auditor-0.1.0a1-py3-none-any.whl
.venv/bin/azure-opsec-auditor --version
```

Windows: use `.venv\Scripts\python.exe` and `.venv\Scripts\azure-opsec-auditor.exe`. No PyPI publication is claimed. Alternatively, run from the checkout without installation:

```sh
python3 -m azure_opsec_auditor fixtures/good.json --as-of 2026-10-09T12:00:00Z
python3 -m azure_opsec_auditor fixtures/bad.json --as-of 2026-10-09T12:00:00Z --format markdown
```

The good example exits 0; the bad example exits 1. `fixtures/unknown.json`, `not_run.json` and `mixed.json` exit 2. Historical `--as-of` is for reproducible examples, not a way to certify stale real data. For current data omit it; default max age is 7 days (`--max-age-days` 1–365). Redirect stdout to a secure local file if needed; do not publish real reports.

The release `examples.zip` includes all synthetic snapshots and the schema. After extraction, the same commands work using the installed `azure-opsec-auditor` entry point. Inputs must conform to [snapshot schema](schemas/snapshot-v1.json); raw tenant exports are not supported. Unknown fields/malformed input are rejected without echoing supplied values. Source states and missing fields preserve unknown/not_run rather than returning a false pass.

## Development and verification

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --require-hashes --only-binary=:all: -r requirements-build.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/check_repository.py
.venv/bin/python -m build --no-isolation
.venv/bin/python scripts/verify_distribution.py
```

Zero runtime dependencies. Build tools are pinned and hash-verified. CI runs the same tests/build/package checks on Linux Python 3.12/3.13. No secrets are needed. See [release procedure](docs/08-release.md) and [managed environment](docs/09-environment.md) for artifacts and remote validation gates.

## Documentation

- [Requirements](docs/01-requirements.md), [threat model](docs/02-threat-model.md), [architecture/schema semantics](docs/03-architecture.md)
- [Exact rule matrix and limitations](docs/04-check-matrix.md), [offline and real lab procedure](docs/05-lab-and-ci.md)
- [Stack ADR](docs/06-adr-stack.md), [MVP plan](docs/07-mvp-plan.md), [release procedure](docs/08-release.md) and [managed environment](docs/09-environment.md)

Never commit real secrets, tenant exports, UPNs or sensitive reports. Use `local-data/` outside public git or a separate protected directory; `.gitignore` is not a security boundary. No paid resources or real credentials are used by development/CI. See [security policy](SECURITY.md).
