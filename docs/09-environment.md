# Development Environment

Use a clean checkout and the runtime version declared by the project. Install
dependencies using [INSTALL.md](../INSTALL.md), then run the formatting, lint,
unit-test, and documentation checks listed in [CONTRIBUTING.md](../CONTRIBUTING.md)
and CI.

Keep credentials and tenant exports outside the source tree. Test live Azure
behavior only in a separate authorized test tenant and document results without
including secrets or customer data.
