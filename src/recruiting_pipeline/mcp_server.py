from __future__ import annotations

import os
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import cast

from mcp.server.fastmcp import FastMCP

from .cli import DEFAULT_CONFIG_PATH
from .config import load_config
from .integrations.obsidian_tracker import write_job_tracker_note
from .job_intake import fetch_job_snapshot, select_relevant_evidence
from .job_workspace import create_job_workspace
from .resume import create_section_resume_proposal, validate_latex_proposal
from .store import PipelineStore


def _json_value(value: object) -> object:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _json_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    return value


def build_server(config_path: Path) -> FastMCP:
    """Build a read-only MCP interface for an existing local pipeline."""
    config = load_config(config_path)
    store = PipelineStore(config.data_dir / "pipeline.sqlite3")
    store.initialize()
    server = FastMCP(
        "Recruiting Pipeline",
        instructions=(
            "Local recruiting context only. These tools are read-only; they never submit "
            "applications, send messages, change mail, or modify resume files."
        ),
    )

    @server.tool()
    def pipeline_status() -> dict[str, int]:
        """Return counts for local-only recruiting records."""
        return {
            "applications": len(store.list_applications()),
            "evidence": len(store.list_evidence()),
            "mail_events": len(store.list_mail_events()),
            "audit_events": len(store.audit_events()),
        }

    @server.tool()
    def list_applications() -> list[dict[str, object]]:
        """List local application records; no external system is queried."""
        return [
            cast(dict[str, object], _json_value(asdict(application)))
            for application in store.list_applications()
        ]

    @server.tool()
    def list_evidence() -> list[dict[str, object]]:
        """List locally stored evidence records used for truthful resume proposals."""
        return [
            cast(dict[str, object], _json_value(asdict(evidence)))
            for evidence in store.list_evidence()
        ]

    @server.tool()
    def list_mail_events() -> list[dict[str, object]]:
        """List normalized local mail events; previews and message bodies are not retained."""
        return [
            cast(dict[str, object], _json_value(asdict(event)))
            for event in store.list_mail_events()
        ]

    @server.tool()
    def prepare_job_workspace(
        job_url: str, company: str, role: str, cycle: str, application_slug: str
    ) -> dict[str, object]:
        """Create a local job package from a URL and return only approved relevant evidence."""
        if config.resume.template_path is None or config.vault_path is None:
            raise ValueError("resume template_path and vault_path must be configured")
        snapshot = fetch_job_snapshot(job_url)
        evidence = select_relevant_evidence(snapshot, store.list_evidence())
        workspace = create_job_workspace(
            output_root=config.resume.output_root,
            cycle=cycle,
            application_slug=application_slug,
            job_url=job_url,
            job_snapshot=snapshot,
            template_path=config.resume.template_path,
            selected_evidence=evidence,
        )
        tracker_note = write_job_tracker_note(
            vault_path=config.vault_path,
            cycle=cycle,
            company=company,
            role=role,
            job_url=job_url,
            package_dir=workspace.package.package_dir,
        )
        return {
            "package_dir": str(workspace.package.package_dir),
            "template_path": str(workspace.template_copy_path),
            "tracker_note": str(tracker_note),
            "evidence": [cast(dict[str, object], _json_value(asdict(item))) for item in evidence],
        }

    @server.tool()
    def create_tailored_resume(
        package_dir: str, section: str, latex_content: str, evidence_ids: list[str]
    ) -> dict[str, str]:
        """Create a reviewable local section proposal using only supplied approved evidence IDs."""
        package = Path(package_dir).expanduser().resolve()
        if package.parent.parent != config.resume.output_root.expanduser().resolve():
            raise ValueError("package_dir must be inside configured output_root")
        if section.casefold() not in {item.casefold() for item in config.resume.editable_sections}:
            raise ValueError("section is not configured as editable")
        proposal = create_section_resume_proposal(
            resume_path=package / "source" / "resume.tex",
            output_dir=package / "artifacts",
            section_name=section,
            latex_content=latex_content,
            evidence=store.approved_evidence(evidence_ids),
        )
        return {
            "proposal_tex": str(proposal.proposed_tex_path),
            "diff": str(proposal.diff_path),
            "claim_report": str(proposal.claim_report_path),
        }

    @server.tool()
    def validate_tailored_resume(proposal_tex: str) -> dict[str, object]:
        """Compile an explicit local proposal; it never publishes or changes the master."""
        validation = validate_latex_proposal(
            Path(proposal_tex), latexmk=Path(config.resume.latexmk)
        )
        return cast(dict[str, object], _json_value(asdict(validation)))

    return server


def main() -> None:
    raw_path = os.environ.get("RECRUITING_PIPELINE_CONFIG")
    config_path = Path(raw_path).expanduser() if raw_path else DEFAULT_CONFIG_PATH
    build_server(config_path).run()


if __name__ == "__main__":
    main()
