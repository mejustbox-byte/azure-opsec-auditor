# Release procedure

Version `0.1.0a1`, Git tag `v0.1.0a1`, prerelease because real platform tests have not run. No PyPI publication or production-readiness claim.

From a clean checkout run the README development commands. Build with pinned hashed tools and `--no-isolation`. `python scripts/release_assets.py` creates `examples.zip` (synthetic snapshots/schema), `documentation.zip` (README/security/docs) and `SHA256SUMS` alongside wheel/sdist in `dist/`. Attach those five assets; GitHub additionally provides source archives. Verify downloaded assets against the manifest before installation. Checksums prove consistency, not publisher identity; obtain them from the same reviewed release.

Create a feature PR, inspect remote CI and merge the reviewed head through GitHub. Do not merge if required CI failed or remains pending. Build release artifacts from the merged commit, tag that exact commit and upload assets. Include supported installation/run commands, rule limits, test results and unperformed Azure/Entra/restore checks in release notes. Inspect release assets/tag/target commit via GitHub API and read-only Git operations. If GitHub operations are unavailable, retain local artifacts and report the blocker; local packaging is not a published release.

Real laboratory prerequisites and outstanding tests: [lab procedure](05-lab-and-ci.md). The CLI has no collector, so platform validation must use a separately approved collection/normalization procedure before any real-data claims.
