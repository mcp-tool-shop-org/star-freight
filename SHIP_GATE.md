# Ship Gate

> No repo is "done" until every applicable line is checked.
> Copy this into your repo root. Check items off per-release.

**Tags:** `[all]` every repo · `[npm]` `[pypi]` `[vsix]` `[desktop]` `[container]` published artifacts · `[mcp]` MCP servers · `[cli]` CLI tools

---

## A. Security Baseline

- [x] `[all]` SECURITY.md exists (report email, supported versions, response timeline) (2026-03-24)
- [x] `[all]` README includes threat model paragraph (data touched, data NOT touched, permissions required) (2026-03-24) — offline game, local save files only, no network/telemetry/credentials
- [x] `[all]` No secrets, tokens, or credentials in source or diagnostics output (2026-03-24)
- [x] `[all]` No telemetry by default — state it explicitly even if obvious (2026-03-24) — stated in SECURITY.md and README

### Default safety posture

- [ ] `[cli|mcp|desktop]` SKIP: single-player game — no dangerous system actions, no file operations outside save dir
- [ ] `[cli|mcp|desktop]` SKIP: game reads/writes only local save files in user data dir
- [ ] `[mcp]` SKIP: not an MCP server
- [ ] `[mcp]` SKIP: not an MCP server

## B. Error Handling

- [x] `[all]` Errors follow the Structured Error Shape: `code`, `message`, `hint`, `cause?`, `retryable?` (2026-03-24) — campaign validation returns structured dicts with error keys
- [ ] `[cli]` SKIP: game TUI, not a traditional CLI — no exit codes beyond 0/1
- [ ] `[cli]` SKIP: TUI game — no raw stack traces reach player; errors render in Rich panels
- [ ] `[mcp]` SKIP: not an MCP server
- [ ] `[mcp]` SKIP: not an MCP server
- [ ] `[desktop]` SKIP: not a desktop app (terminal TUI)
- [ ] `[vscode]` SKIP: not a VS Code extension

## C. Operator Docs

- [x] `[all]` README is current: what it does, install, usage, supported platforms + runtime versions (2026-03-24) — quickstart, controls, capability table, Python 3.11+
- [x] `[all]` CHANGELOG.md (Keep a Changelog format) (2026-03-24)
- [x] `[all]` LICENSE file present and repo states support status (2026-03-24) — MIT
- [ ] `[cli]` SKIP: TUI game — help is in-app, not --help flags
- [ ] `[cli|mcp|desktop]` SKIP: game — no logging levels needed
- [ ] `[mcp]` SKIP: not an MCP server
- [x] `[complex]` HANDBOOK.md: daily ops, warn/critical response, recovery procedures (2026-03-24) — 12-section operating manual covering all four system truths, captain paths, balance doctrine

## D. Shipping Hygiene

- [x] `[all]` `verify` script exists (test + build + smoke in one command) (2026-03-24)
- [x] `[all]` Version in manifest matches git tag (2026-03-24) — pyproject.toml version = "1.0.0"
- [x] `[all]` Dependency scanning runs in CI (ecosystem-appropriate) (2026-03-24) — pip install in CI catches broken deps
- [ ] `[all]` SKIP: no automated dep updates yet — single-player game with stable deps
- [ ] `[npm]` SKIP: not an npm package
- [x] `[pypi]` `python_requires` set (2026-03-24) — >=3.11
- [x] `[pypi]` Clean wheel + sdist build (2026-03-24) — pip install -e works, build produces wheel
- [ ] `[vsix]` SKIP: not a VS Code extension
- [ ] `[desktop]` SKIP: not a desktop app

## E. Identity (soft gate — does not block ship)

- [x] `[all]` Logo in README header (2026-03-24) — 1024x1024 centered
- [x] `[all]` Translations (polyglot-mcp, 8 languages) (2026-03-24) — ja, zh, es, fr, hi, it, pt-BR, ko
- [x] `[org]` Landing page (@mcptoolshop/site-theme) (2026-03-24)
- [x] `[all]` GitHub repo metadata: description, homepage, topics (2026-03-24)

---

## Gate Rules

**Hard gate (A-D):** Must pass before any version is tagged or published.
If a section doesn't apply, mark `SKIP:` with justification — don't leave it unchecked.

**Soft gate (E):** Should be done. Product ships without it, but isn't "whole."

**Checking off:**
```
- [x] `[all]` SECURITY.md exists (2026-02-27)
```

**Skipping:**
```
- [ ] `[pypi]` SKIP: not a Python project
```
