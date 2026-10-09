# Threat model

Assets: local normalized metadata, reports, public code/release integrity and operator trust. Current boundaries: local file → strict parser → pure rules → stdout → operator-controlled destination. CI/build/release are separate trust boundaries. No auth or Graph/ARM transport exists in the MVP.

| Threat | Implemented control | Test / residual risk |
|---|---|---|
| Malformed/ambiguous input | strict schema, duplicate-key rejection, type/range/size bounds, UTF-8 only | parser/schema negative tests; local attacker can still supply false valid metadata |
| Report injection or payload disclosure on error | bounded ASCII identifiers/enumerated fields; errors never include values/unknown keys | error/no-echo and invalid-string tests; valid pseudonyms and permitted metadata are intentionally reported |
| False assurance from missing data | unknown/not_run coverage, explicit source state, freshness budget, record-only pass semantics | partial/missing/stale tests; operator completeness/normalization assertions cannot be independently verified |
| Accidental cloud action | no cloud/network/auth dependency or collector | socket-denial unit test; shell/user tooling is outside the auditor |
| Disclosure in public git/artifacts | synthetic examples, ignored local-data/reports/secrets, repository signature scan and manual diff/artifact inspection | best-effort checks; signature scanning cannot prove absence of every secret or sensitive metadata |
| Supply chain | zero runtime dependencies; hashed build wheels; pinned Actions; contents:read; no PR secrets | wheel install smoke and CI; trusted tooling/runner can still be compromised |
| Denial of service | 5 MiB input, 1000 records/source, 50 list items, bounded strings and recursion errors | limits tests; local file I/O or output consumer may block |
| Stale evidence / clock manipulation | UTC observation/as-of and bounded age budget | boundary tests; historical replay intentionally trusts operator-selected as-of |

Future live collectors additionally require token/tenant/audience validation, minimally scoped credentials, verb/host/path allowlists, guarded nextLink/redirects, bounded retries/pages and redacted logs. Those controls are design requirements, not implemented transport guarantees. A compromised snapshot can hide risk despite passing all schema checks.

If a credential or real tenant export leaks: stop publication, restrict evidence, revoke the credential via the owner, review history/artifacts and follow the incident procedure. Deleting a file alone is insufficient. This project is an advisory metadata checker, not an enforcement or recovery system.
