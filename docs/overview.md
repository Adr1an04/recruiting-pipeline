# Erga MCP overview

Erga is a local-first career and recruiting workspace. It organizes evidence, job research,
application state, recruiting-mail metadata, and reviewable résumé proposals without taking over
the user's consequential decisions.

## The problem

A job search scatters facts and repetitive work across résumés, job postings, mailboxes, notes,
trackers, and application portals. Generative tools often make that fragmentation worse by
producing text without durable provenance or by asking for broad access to sensitive accounts.

Erga treats the workflow as a local information system instead:

- career facts have sources and approval state;
- job intake creates an isolated package with bounded source material;
- application and mail events have normalized local records;
- résumé changes are artifacts to review, not silent edits; and
- optional agent integrations call the same deterministic core as the CLI.

## System shape

Erga has three layers:

1. **Local core** — models, SQLite storage, classification, evidence validation, job intake, résumé
   proposals, reporting, and export.
2. **User interfaces** — the `erga` CLI and `erga-mcp` local stdio server.
3. **Optional adapters** — read-only Gmail and Zoho access, Obsidian imports and tracker notes,
   Hermes routing, and private scheduled notifications.

The adapters are not the product core. Removing Hermes, MCP, or every mail connector still leaves
a useful standalone application.

## Product boundary

Erga may read user-authorized sources, create local records, generate research, reorder existing
résumé content, compile a proposal, and export private state when explicitly requested.

Erga does not submit applications, fill forms, send messages, mutate mail, invent experience,
guess missing metrics, or synchronize a remote résumé without a separately designed and explicit
user-authorized action.

## Where to go next

- Follow [`getting-started.md`](getting-started.md) to run Erga.
- Read the [core architecture decision](architecture/ADR-001-local-core-and-evidence-ledger.md).
- Review [`security.md`](security.md) before enabling integrations.
- See [`FUTURE.md`](FUTURE.md) for planned work and non-goals.
