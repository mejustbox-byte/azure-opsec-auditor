#!/usr/bin/env bash
# Reproducible developer setup; no cloud credentials or preserved venv required.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
python3 -c 'import sys; assert sys.version_info >= (3, 12), "Python >=3.12 required"'
OPSEC_VENV_DIR="${OPSEC_VENV_DIR:-.venv}"
python3 -m venv "$OPSEC_VENV_DIR"
"$OPSEC_VENV_DIR/bin/python" -m pip install --require-hashes --only-binary=:all: -r requirements-build.txt
"$OPSEC_VENV_DIR/bin/python" -m pip install --no-build-isolation --no-deps -e .
"$OPSEC_VENV_DIR/bin/python" -m pip check
"$OPSEC_VENV_DIR/bin/python" -m unittest discover -s tests -v
"$OPSEC_VENV_DIR/bin/python" scripts/check_repository.py
"$OPSEC_VENV_DIR/bin/azure-opsec-auditor" fixtures/good.json --as-of 2026-10-09T12:00:00Z > /dev/null
