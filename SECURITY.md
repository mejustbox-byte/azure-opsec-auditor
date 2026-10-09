# Security policy

This alpha is an offline normalized-metadata checker. It is not a live collector, enforcement tool or proof of tenant security. All platform/restore behavior remains unverified.

Do not post credentials, real tenant exports, identifiers or sensitive findings to public issues/PRs. Use GitHub private vulnerability reporting if enabled by the owner; otherwise arrange a private reporting channel with the owner before sharing sensitive details. Do not assume a public issue is private. Report a minimal synthetic reproduction.

For development and release: no real credentials, production tenant exports, Azure resource creation, cloud login or mutation. Build dependencies use exact hashes and Actions use reviewed commit pins. Repository scanning is best effort and requires human review; it does not guarantee absence of every secret.
