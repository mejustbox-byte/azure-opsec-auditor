# Managed development environment

The product and all required documentation live in `/workspace/azure-opsec-auditor`. No onboarding directory or retained virtual environment is required. Use the existing isolated checkout; do not create a Git worktree unless explicitly requested. No services, Docker, Azure CLI, login or cloud credentials are required.

## Install / refresh
From the checkout run `bash scripts/install.sh`. It checks Python >=3.12, creates `.venv` if absent, installs exact hash-locked build tools and the local editable product without build isolation/runtime dependency resolution, checks pip consistency, runs unit/CLI integration tests and repository scanning, and invokes the installed CLI on the synthetic good fixture.

To prove independent setup, create a new temporary directory and run `OPSEC_VENV_DIR=/absolute/new/path bash scripts/install.sh`; do not reuse a previous venv for this check. Linux/bash instructions are the managed-environment contract. README also documents platform-neutral manual package installation; Windows managed setup is not tested.

## Task startup
Run `.venv/bin/azure-opsec-auditor --version`; if missing, run installation. From the checkout execute `.venv/bin/python -m unittest discover -s tests -v` and `.venv/bin/python scripts/check_repository.py`. Use `fixtures/good.json --as-of 2026-10-09T12:00:00Z` for an expected exit-0 example; bad=1, unknown/not_run/mixed=2. No persistent processes need restarting.

## Build / distribution readiness
Run `.venv/bin/python -m build --no-isolation`, `.venv/bin/python scripts/verify_distribution.py` and `.venv/bin/python scripts/release_assets.py`. Signature/link scans and isolated wheel/sdist checks are local evidence, not remote CI or real Azure validation. Never add credentials, tenant exports or real reports to public git or artifacts.

Environment `install_script` should contain `set -euo pipefail`, `cd /workspace/azure-opsec-auditor`, `bash scripts/install.sh`. `start_skill` describes the startup checks above and the implemented product. Save the actual checkout commit in the environment repository configuration; until PR merge, restore the feature commit rather than the old README-only main. Saving the draft does not apply, publish or validate a fresh cloud task. After reviewing/saving/publishing settings, verify restoration and repeat the startup checks in a new task.

GitHub API/upload domains may be allowed for authorized repository operations; no credential values are stored in setup. Git read/write and GitHub API access have separate authorization behavior. For this task, standard `git -c credential.helper='!gh auth git-credential' push` used the already supplied authentication successfully without revealing it; do not extract tokens or bypass authentication if a future operation fails. Missing MCP/API access must be reported to the managing chat.
