from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from dataclasses import asdict
from pathlib import Path

from .config import DEFAULT_CONFIG, load_config
from .integrations.obsidian import import_markdown_evidence
from .integrations.zoho import ingest_fixture
from .resume import create_resume_proposal, validate_latex_proposal
from .store import PipelineStore

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "recruiting-pipeline" / "config.toml"


def _config_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="recruiting-pipeline",
        description=(
            "Local-first recruiting workflow tools. No external actions are performed by default."
        ),
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    init = subcommands.add_parser(
        "init", help="create a local non-secret configuration and database"
    )
    _config_argument(init)

    status = subcommands.add_parser("status", help="show local pipeline counts")
    _config_argument(status)

    evidence = subcommands.add_parser("evidence", help="manage local evidence records")
    evidence_commands = evidence.add_subparsers(dest="evidence_command", required=True)
    evidence_add = evidence_commands.add_parser("add", help="add local career evidence")
    _config_argument(evidence_add)
    evidence_add.add_argument("--source-ref", required=True)
    evidence_add.add_argument("--text", required=True)
    evidence_add.add_argument("--approved", action="store_true")

    obsidian = subcommands.add_parser("obsidian", help="import configured Obsidian evidence")
    obsidian_commands = obsidian.add_subparsers(dest="obsidian_command", required=True)
    obsidian_import = obsidian_commands.add_parser(
        "import", help="read a configured Markdown note without modifying the vault"
    )
    _config_argument(obsidian_import)
    obsidian_import.add_argument("--note", type=Path, required=True)

    zoho = subcommands.add_parser("zoho", help="run bounded local Zoho adapter checks")
    zoho_commands = zoho.add_subparsers(dest="zoho_command", required=True)
    zoho_fixture = zoho_commands.add_parser(
        "ingest-fixture", help="classify local synthetic metadata without OAuth or network access"
    )
    _config_argument(zoho_fixture)
    zoho_fixture.add_argument("--fixture", type=Path, required=True)

    resume = subcommands.add_parser("resume", help="create reviewable local resume proposals")
    resume_commands = resume.add_subparsers(dest="resume_command", required=True)
    resume_propose = resume_commands.add_parser(
        "propose", help="create a local proposal without modifying or syncing the source"
    )
    _config_argument(resume_propose)
    resume_propose.add_argument("--resume", type=Path, required=True)
    resume_propose.add_argument("--output-dir", type=Path, required=True)
    resume_propose.add_argument("--latex-snippet", required=True)
    resume_propose.add_argument("--evidence-id", action="append", default=[])
    resume_validate = resume_commands.add_parser(
        "validate",
        help="compile an explicitly selected local proposal without remote synchronization",
    )
    _config_argument(resume_validate)
    resume_validate.add_argument("--proposal", type=Path, required=True)
    resume_validate.add_argument("--latexmk", type=Path, default=Path("latexmk"))

    applications = subcommands.add_parser("applications", help="manage local applications")
    _config_argument(applications)
    application_commands = applications.add_subparsers(dest="applications_command", required=False)
    applications_list = application_commands.add_parser("list", help="list applications")
    _config_argument(applications_list)
    applications_add = application_commands.add_parser("add", help="add a draft application")
    _config_argument(applications_add)
    applications_add.add_argument("--company", required=True)
    applications_add.add_argument("--role", required=True)
    applications_add.add_argument("--source-url", required=True)
    applications_add.add_argument("--evidence-id", action="append", default=[])
    return parser


def _initialize(config_path: Path) -> int:
    config_path = config_path.expanduser()
    if config_path.exists():
        print(f"Config already exists: {config_path}")
        return 2
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(DEFAULT_CONFIG, encoding="utf-8")
    config = load_config(config_path)
    PipelineStore(config.data_dir / "pipeline.sqlite3").initialize()
    print(f"Created local configuration: {config.config_path}")
    print(f"Created local data directory: {config.data_dir}")
    return 0


def _store_for(config_path: Path) -> PipelineStore:
    config = load_config(config_path)
    store = PipelineStore(config.data_dir / "pipeline.sqlite3")
    store.initialize()
    return store


def _print_json(value: object) -> None:
    print(json.dumps(value, default=str, sort_keys=True))


def main(arguments: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(arguments)
    if args.command == "init":
        return _initialize(args.config)

    store = _store_for(args.config)
    if args.command == "status":
        _print_json(
            {
                "applications": len(store.list_applications()),
                "audit_events": len(store.audit_events()),
                "evidence": len(store.list_evidence()),
                "mail_events": len(store.list_mail_events()),
            }
        )
        return 0
    if args.command == "evidence" and args.evidence_command == "add":
        evidence = store.add_evidence(
            source_ref=args.source_ref, text=args.text, approved=args.approved
        )
        _print_json(asdict(evidence))
        return 0
    if args.command == "obsidian" and args.obsidian_command == "import":
        config = load_config(args.config)
        if config.vault_path is None:
            raise ValueError("vault_path must be configured before importing Obsidian evidence")
        imported = [
            store.add_evidence(source_ref=item.source_ref, text=item.text, approved=False)
            for item in import_markdown_evidence(config.vault_path, args.note)
        ]
        _print_json([asdict(item) for item in imported])
        return 0
    if args.command == "zoho" and args.zoho_command == "ingest-fixture":
        _print_json({"created": ingest_fixture(store, args.fixture)})
        return 0
    if args.command == "resume" and args.resume_command == "propose":
        proposal = create_resume_proposal(
            resume_path=args.resume,
            output_dir=args.output_dir,
            latex_snippet=args.latex_snippet,
            evidence=store.approved_evidence(args.evidence_id),
        )
        _print_json(asdict(proposal))
        return 0
    if args.command == "resume" and args.resume_command == "validate":
        _print_json(asdict(validate_latex_proposal(args.proposal, latexmk=args.latexmk)))
        return 0
    if args.command == "applications":
        if args.applications_command == "add":
            application = store.create_application(
                company=args.company,
                role=args.role,
                source_url=args.source_url,
                evidence_ids=args.evidence_id,
            )
            _print_json(asdict(application))
            return 0
        _print_json([asdict(application) for application in store.list_applications()])
        return 0
    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
