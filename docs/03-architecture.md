# Architecture

Implemented pipeline: `CLI → bounded UTF-8 JSON loader → schema validator → pure rule engine → JSON/Markdown stdout`. No networking, authentication, background services or Azure SDK. Each catalog entry defines fields, severity, risk predicate, remediation and limitations. `schema.py` generates the checked-in JSON Schema and validates the supported subset using only stdlib.

## Input contract
Root: `schema_version:1`, `synthetic:boolean`, pseudonymous `scope`, UTC `collected_at`, `sections`. Each named section: `status` (complete/partial/unavailable/not_run), `source`, `api_version`, `records`. A record has unique `id` within its section and the fields in the rule matrix. Nullable or absent rule fields represent unavailable evidence; id is required. Unknown fields are rejected. Unavailable/not_run sections must have no records. Empty complete sections still yield unknown rather than asserting safe coverage.

One snapshot timestamp applies to all included records: an operator must not combine newer and older evidence under a newer timestamp. Use the oldest collection timestamp or split snapshots. JSON Schema covers structural restrictions; runtime additionally enforces unique record IDs, calendar-valid UTC timestamps, no duplicate JSON keys and a freshness budget. The schema artifact is shipped separately in the release.

## Findings and coverage
One finding per record; extra coverage finding for partial/empty source. Missing source gives not_run. Stale available source gives unknown and no record findings. If any required rule field is missing/null, the record is unknown even if another field looks risky; this conservative MVP can suppress known risk when normalization is incomplete. Complete records are evaluated in stable rule/record order. Findings include source/API/rule versions, evidence fields, confidence, severity, rationale, limitations and suggested manual remediation. Evidence is normalized supplied metadata, not raw API responses.

Exit status 2 for unknown/not_run or input error, otherwise 1 for fail, otherwise 0. `--as-of` pins historical replay; the default is current UTC. Default max age is seven days, configurable 1–365. Future timestamps are invalid. No output file options: the operator controls shell redirection and access permissions.

## Future live boundary — not implemented
Graph: directory roles/PIM, CA/auth strengths, service principals, permission grants, federation and registration reports. ARM: resource RBAC/PIM, identities, vaults, storage, NSGs, diagnostics and backup metadata. Plan auth adapter and collection transport separately from the pure rules. No default credential chain or silent tenant switching. Exact endpoint-specific permissions and license behavior require a separate test tenant; do not assume ARM Reader or a single broad Graph grant covers every source. No listKeys or secret-content APIs.
