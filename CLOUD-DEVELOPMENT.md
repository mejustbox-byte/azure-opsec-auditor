# Development Environment

Use a clean checkout of the default branch and the runtime version declared in
`pyproject.toml` or `.python-version`. Install the project and development
dependencies with the commands documented in [INSTALL.md](INSTALL.md), then run
the checks listed in [CONTRIBUTING.md](CONTRIBUTING.md) and the repository's CI.

Keep credentials, customer data, production exports, and generated reports
outside the source tree. A passing local or CI check validates only the checks
it runs; platform-specific behavior and deployment require separate documented
validation.
