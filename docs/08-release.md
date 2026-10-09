# Release procedure

Version `0.1.0a1`, Git tag `v0.1.0a1`, prerelease because real platform tests have not run. No PyPI publication or production-readiness claim.

From a clean checkout run the README development commands. Build with pinned hashed tools and `--no-isolation`. `python scripts/release_assets.py` creates `examples.zip` (synthetic snapshots/schema), `documentation.zip` (README/security/docs) and `SHA256SUMS` alongside wheel/sdist in `dist/`. Attach those five assets; GitHub additionally provides source archives. Verify downloaded assets against the manifest before installation. Checksums prove consistency, not publisher identity; obtain them from the same reviewed release.

Create a feature PR, inspect remote CI and merge the reviewed head through GitHub. Do not merge if required CI failed or remains pending. Build release artifacts from the merged commit, tag that exact commit and upload assets. Include supported installation/run commands, rule limits, test results and unperformed Azure/Entra/restore checks in release notes. Inspect release assets/tag/target commit via GitHub API and read-only Git operations. If GitHub operations are unavailable, retain local artifacts and report the blocker; local packaging is not a published release.

Real laboratory prerequisites and outstanding tests: [lab procedure](05-lab-and-ci.md). The CLI has no collector, so platform validation must use a separately approved collection/normalization procedure before any real-data claims.

## Standard Actions publication path

When cloud proxy credentials cannot authorize uploads.github.com, use `.github/workflows/release.yml` on reviewed main with the repository-provided job-scoped GITHUB_TOKEN. No new secret or credential binding is needed. Merge the workflow through its own PR and green CI before dispatch.

The manual dispatch accepts an existing alpha tag and an approved full commit SHA. Validation rejects branch names, malformed refs, version mismatches, changed tags and commits outside main ancestry. Checkout pins are the verified official versions; checkout does not persist credentials. The only write grant is `contents:write` on the release job; GH_TOKEN is exposed only to its final upload/publication step. The workflow does not create/reset/push tags.

It builds and tests the exact tag, normalizes archive container metadata for reproducible retries, validates installed wheel/sdist, creates synthetic/documentation assets and SHA256SUMS, and verifies existing assets before upload without clobber. An existing prerelease draft with matching target is required. It downloads/checks all five assets before publishing, verifies publication/tag/inventory, then downloads/checks them again. A completed published release with matching assets is a read-only successful retry; unexpected/different assets or a stable release abort.

Dispatch: `gh workflow run release.yml --repo mejustbox-byte/azure-opsec-auditor --ref main -f tag=v0.1.0a1 -f expected_commit=698372c2b6f54707561da22e3f9ac52668c2e4a5`. Observe the actual run and its verified published assets before claiming success. The existing v0.1.0a1 tag remains on the product merge commit even though automation lives in a later reviewed main commit.
