<div align="center">
  <img src="docs/assets/erga-logo.svg" width="720" alt="Erga" />

  <p><strong>Your private, evidence-first career workspace.</strong></p>

  <p>
    Local-first&nbsp;&nbsp;·&nbsp;&nbsp;Reviewable&nbsp;&nbsp;·&nbsp;&nbsp;MCP-ready
  </p>

  <p>
    <a href="https://github.com/Adr1an04/erga-mcp/actions/workflows/ci.yml"><img src="https://github.com/Adr1an04/erga-mcp/actions/workflows/ci.yml/badge.svg" alt="CI" /></a>
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white" alt="Python 3.11+" /></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-C8792A.svg" alt="MIT License" /></a>
    <img src="https://img.shields.io/badge/Status-Pre--Alpha-F2A93B.svg" alt="Pre-Alpha" />
  </p>

  <p>
    <a href="#quick-start">Quick start</a> ·
    <a href="#how-erga-works">How it works</a> ·
    <a href="docs/getting-started.md">Documentation</a> ·
    <a href="CONTRIBUTING.md">Contributing</a>
  </p>
</div>

---

**Erga** comes from the Greek word for works or deeds. The project handles the repetitive work
around a job search while keeping consequential decisions in your hands.

Erga MCP is an open-source Python CLI and local MCP server that turns verified career evidence,
job postings, recruiting mail, and a user-provided LaTeX résumé into an organized, reviewable
workflow. Its core is deterministic and local: SQLite state, auditable records, bounded imports,
and résumé diffs you approve yourself.

> [!IMPORTANT]
> Erga prepares research and local drafts. It does not submit applications, send messages, invent
> résumé claims, mutate email, or update a remote résumé on its own.

## Principles

1. **Evidence before generation** — every new résumé claim must trace to career evidence supplied
   and approved by the user.
2. **Local by default** — application state, evidence, and generated artifacts remain in paths you
   control.
3. **Review before action** — résumé changes are separate proposals with a diff and claim report.
4. **Narrow integrations** — mail access is read-only, MCP runs over stdio, and optional adapters
   receive only the capabilities they need.
5. **Deterministic core** — the standalone CLI and domain layer work without an agent, hosted
   service, or proprietary UI.

## What Erga does

| Capability | Result |
| --- | --- |
| Career evidence | Stores verified facts with provenance and approval state |
| Job intake | Captures a public posting and creates an isolated local workspace |
| Résumé tailoring | Reorders existing, user-written content and creates a reviewable diff |
| Claim validation | Links proposed claims to approved evidence instead of inventing metrics |
| Recruiting mail | Classifies bounded Gmail or Zoho metadata using local rules |
| Application tracking | Keeps draft applications, status history, and an audit trail in SQLite |
| MCP integration | Exposes the same workflow to Hermes and other compatible clients |
| Private export | Packages local records and generated job artifacts into an explicit ZIP export |

Erga intentionally does **not** fill forms, submit applications, send recruiter messages, modify
mailboxes, or silently overwrite your résumé.

## How Erga works

```text
verified career facts ───────┐
                             ▼
job posting ─────────► evidence ledger ─────► draft application
                             │
read-only mail metadata ─────┤
                             ▼
                  local job workspace
                             │
                             ▼
              résumé proposal + diff + claim report
                             │
                             ▼
                        you review
```

Automatic tailoring is deliberately narrow. Erga ranks and reorders existing Experience bullets,
project entries, and skills against visible job-posting content. It does not rewrite those claims.
Generated packages record the source and output position of each claim, matched terms, and exact
evidence references when available.

## Quick start

### Requirements

- Python 3.11 or newer
- [`uv`](https://docs.astral.sh/uv/)
- Git

Optional workflows use `latexmk`, an existing LaTeX résumé, a supported operating-system
credential store, or an authenticated [`gws`](https://github.com/googleworkspace/cli) command.

### Install

```bash
git clone https://github.com/Adr1an04/erga-mcp.git
cd erga-mcp
uv sync --extra mcp
```

Initialize a private local workspace and verify the installation:

```bash
uv run erga init
uv run erga doctor
```

By default Erga creates:

```text
~/.config/erga-mcp/
├── config.toml
└── state/
    └── erga.sqlite3
```

The configuration contains paths and feature settings, never credentials. Use
`--config /absolute/path/to/config.toml` to select another location.

### Add evidence and a draft application

```bash
uv run erga evidence add \
  --source-ref 'Career.md#Pipeline project' \
  --text 'Built a Python pipeline that reduced weekly manual review by 30%.' \
  --approved
```

Use the returned evidence ID to create a local draft:

```bash
uv run erga applications add \
  --company 'Example Company' \
  --role 'Software Engineer' \
  --source-url 'https://jobs.example.com/123' \
  --evidence-id 'ev_a1b2...'
```

Nothing is sent to the employer. Check local state with:

```bash
uv run erga status
uv run erga applications list
```

For résumé setup, mail connectors, job-link routing, and scheduled private alerts, continue with
the [complete getting-started guide](docs/getting-started.md).

## MCP and Hermes

Install the optional MCP dependencies, then register the local stdio server:

```bash
uv sync --extra mcp

hermes mcp add erga-mcp \
  --command "uv --directory /absolute/path/to/erga-mcp run erga-mcp"
```

Set `ERGA_MCP_CONFIG` in the MCP environment to the absolute path of your local `config.toml`.
See [`integrations/hermes/mcp.example.yaml`](integrations/hermes/mcp.example.yaml) for a complete
example.

Core MCP tools include:

| Tool | Behavior |
| --- | --- |
| `pipeline_status` | Read local record counts |
| `list_applications` | Read local application records |
| `list_evidence` | Read local evidence records |
| `list_mail_events` | Read normalized local mail events |
| `intake_job_url` | Research one job and build local review artifacts end to end |
| `prepare_job_workspace` | Create a bounded local job package from a supplied URL |
| `create_tailored_resume` | Create a proposal, diff, and evidence report |
| `validate_tailored_resume` | Run the configured local LaTeX compiler |
| `install_mail_monitor_scripts` | Prepare deterministic Hermes notification runners |
| `export_data` | Build a private ZIP of local records and generated packages |

Local-write and local-exec tools remain subject to approval in the invoking MCP client. The full
capability model is documented in [`docs/security.md`](docs/security.md).

## Repository map

```text
src/erga_mcp/          deterministic domain layer, CLI, and MCP server
integrations/hermes/  optional Hermes configuration and router plugin
skills/productivity/  optional workflow skill
cron/                 private notification runner documentation
docs/                 architecture, security, setup, and project direction
tests/                synthetic unit and MCP integration tests
```

## Documentation

Start here, in order:

1. [`docs/overview.md`](docs/overview.md) — product boundary and system shape.
2. [`docs/getting-started.md`](docs/getting-started.md) — full local and integration setup.
3. [`docs/architecture/ADR-001-local-core-and-evidence-ledger.md`](docs/architecture/ADR-001-local-core-and-evidence-ledger.md) — core architecture decision.
4. [`docs/security.md`](docs/security.md) — trust boundaries and MCP capability model.
5. [`CONTRIBUTING.md`](CONTRIBUTING.md) — development workflow and acceptance checks.
6. [`docs/FUTURE.md`](docs/FUTURE.md) — roadmap and explicit non-goals.
7. [`docs/versioning.md`](docs/versioning.md) — pre-1.0 release policy.

## Project status

Erga MCP is **pre-alpha**. The evidence ledger, local application store, deterministic mail
classification, job workspace creation, LaTeX proposal artifacts, read-only mail connectors, and
MCP surface are implemented and tested. Breaking changes are expected before 1.0.

Current limitations:

- no graphical interface;
- no automatic matching between mail events and application records;
- imported Obsidian candidates cannot yet be approved through the CLI;
- relevance ranking is lexical rather than semantic;
- résumé workflows currently target LaTeX; and
- no remote résumé synchronization or automatic job submission by design.

## Development

```bash
uv sync --extra mcp --extra dev
uv run ruff format --check .
uv run ruff check .
uv run mypy src
uv run python -m unittest discover -s tests -v
uv build
git diff --check
```

Tests and examples use synthetic data. Never commit real résumés, applications, email content,
credentials, contact details, exports, or vault contents.

## Contributing

Issues and pull requests are welcome. Read [`CONTRIBUTING.md`](CONTRIBUTING.md), follow the
[`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md), and use private vulnerability reporting described in
[`SECURITY.md`](SECURITY.md).

## License

Erga MCP is available under the [MIT License](LICENSE).
