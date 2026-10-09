# Requirements / GITHUB-OPSEC Azure and Entra

Status: implemented offline MVP `0.1.0a1`; no live collector. The broader product direction remains read-only RBAC/PIM, Conditional Access, phishing-resistant MFA, workload/service principals, OAuth, managed identities/OIDC, Key Vault, anonymous storage/network exposure, logging and recovery.

## MVP acceptance requirements
- R1: local CLI with no authentication, network calls, resource creation or mutation. Only stdout/stderr output; input is unchanged.
- R2: normalized version-1 schema, not a raw Graph/ARM export. Reject unknown properties, duplicates, invalid types/enums, unsafe identifiers, nonfinite numbers, excessive sizes and invalid timestamps without echoing payloads.
- R3: twelve explicit, narrow rules with good/bad/unknown/not_run synthetic cases. Findings include record identity, evidence, severity, source/API version, observation time, rule version, reason, remediation and limitations.
- R4: absent source → not_run; unavailable, partial, empty, stale or incomplete required evidence → unknown. Known records from a partial source can have findings, but an additional unknown coverage finding remains.
- R5: deterministic JSON/Markdown for the same input, `--as-of` and freshness budget. No global secure/insecure badge. A pass proves only that the narrow risk predicate was false for the supplied record.
- R6: exit 0 complete/no failures, 1 complete/at least one failure, 2 invalid input or incomplete evidence (takes precedence over 1). Errors produce no partial report; valid but incomplete input produces a report.
- R7: zero runtime dependencies; pinned, hash-verified build dependencies; wheel/sdist and SHA256 manifest. Unit/integration tests and least-privilege CI, no cloud credentials.

## Boundary and backlog
MVP accepts pseudonymous normalized local metadata, including `synthetic:false` for future operator-supplied lab data. It cannot establish provenance, permission correctness, scope completeness, group membership, policy applicability, effective network reachability or restore success. A source status of complete is an operator assertion, not an independently verified fact.

Future collectors require explicit tenant/subscription allowlists, minimally scoped auth, Graph/ARM audiences, pagination and Retry-After budgets, safe nextLink host validation, stable API preference and endpoint-specific permissions/licensing. Live integration is NOT VERIFIED. No automatic remediation, secret/key/certificate contents, blob downloads, port scanning, production tenant collection or paid resources in this release.

The intended full product needs group/role inheritance, custom roles, both Entra/Azure PIM planes, effective CA coverage and emergency exclusions, auth registration vs session enforcement, delegated/application permission resolution, identity/resource association, effective ACL/private endpoint evaluation, diagnostic delivery and independent restore testing. These must not be inferred from the MVP's simplified fields.

## Data handling
Public repository/artifacts: synthetic examples only. Do not place tenant exports, identifiers, UPNs, credentials or sensitive evidence in public git/CI artifacts. Local real normalized snapshots/reports require operator-controlled access and retention outside the checkout. Run offline; do not pipe untrusted snapshots into public issue/report uploads.
