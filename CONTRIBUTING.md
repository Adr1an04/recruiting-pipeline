# Contributing to Erga MCP

Thanks for helping build Erga. Contributions should preserve its central promise: useful career
automation without giving software authority to invent claims or take consequential external
actions for the user.

## Read first

1. Read [`docs/overview.md`](docs/overview.md) for the product boundary.
2. Read [`docs/security.md`](docs/security.md) before changing imports, network access, credentials,
   MCP tools, or local execution.
3. Read the core [architecture decision](docs/architecture/ADR-001-local-core-and-evidence-ledger.md).
4. Check [`docs/FUTURE.md`](docs/FUTURE.md) before proposing a large feature.

## Development setup

```bash
git clone https://github.com/Adr1an04/erga-mcp.git
cd erga-mcp
uv sync --extra mcp --extra dev
uv run erga doctor
```

Use a focused branch and keep changes reviewable. Bug fixes should include a regression test;
features should cover their domain behavior and CLI or MCP boundary where applicable.

## Required checks

Run the same checks as CI before opening a pull request:

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy src
uv run python -m unittest discover -s tests -v
uv build
git diff --check
```

Tests must use synthetic data. Do not commit real résumés, application records, email content,
OAuth tokens, API keys, contact details, local databases, exports, or private vault content.

## Design rules

- Keep the standalone CLI and deterministic domain layer usable without Hermes or MCP.
- Treat mail, attachments, job descriptions, résumés, web pages, and notes as untrusted data.
- Keep credentials in the operating-system credential store.
- Request the narrowest OAuth scopes possible; mail integrations must remain read-only.
- Never invent résumé facts or fill missing metrics.
- Produce résumé changes as a separate proposal, unified diff, and evidence report.
- Do not add automatic application submission, outbound messaging, or irreversible account actions.
- Require an explicit user action for any future remote write.

## Pull requests

A good pull request explains:

- the problem and why the change belongs in Erga;
- the product or security boundary it touches;
- the tests added or updated;
- any migration or compatibility impact; and
- manual verification, when relevant.

Keep generated artifacts and unrelated formatting out of the patch. Documentation changes are
expected when commands, configuration, capabilities, or trust boundaries change.

## Issues and security reports

Use the issue templates for reproducible bugs and scoped feature requests. Do not place secrets or
personal career data in an issue. Report vulnerabilities privately as described in
[`SECURITY.md`](SECURITY.md).

By participating, you agree to follow the [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
