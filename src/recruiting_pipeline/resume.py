from __future__ import annotations

import difflib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .models import Evidence


@dataclass(frozen=True)
class ResumeProposal:
    proposed_tex_path: Path
    diff_path: Path
    claim_report_path: Path


@dataclass(frozen=True)
class LatexValidation:
    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


_DISALLOWED_LATEX = ("\\input", "\\include", "\\write18", "\\immediate\\write")


def create_resume_proposal(
    *, resume_path: Path, output_dir: Path, latex_snippet: str, evidence: list[Evidence]
) -> ResumeProposal:
    """Create review artifacts beside local state; never modify or sync the resume source."""
    if resume_path.suffix.lower() != ".tex":
        raise ValueError("resume_path must point to a .tex file")
    if not evidence or any(not item.approved for item in evidence):
        raise ValueError("a resume proposal requires approved evidence")
    if not latex_snippet.strip():
        raise ValueError("latex_snippet cannot be empty")
    if any(marker in latex_snippet for marker in _DISALLOWED_LATEX):
        raise ValueError("latex_snippet contains a disallowed file or shell command")

    original = resume_path.read_text(encoding="utf-8")
    proposed = f"{original.rstrip()}\n\n% Recruiting Pipeline proposal\n{latex_snippet.strip()}\n"
    output_dir.mkdir(parents=True, exist_ok=True)
    proposed_tex_path = output_dir / "proposal.tex"
    diff_path = output_dir / "proposal.diff"
    claim_report_path = output_dir / "claim-report.json"

    proposed_tex_path.write_text(proposed, encoding="utf-8")
    diff_path.write_text(
        "".join(
            difflib.unified_diff(
                original.splitlines(keepends=True),
                proposed.splitlines(keepends=True),
                fromfile=str(resume_path),
                tofile=str(proposed_tex_path),
            )
        ),
        encoding="utf-8",
    )
    claim_report_path.write_text(
        json.dumps(
            {
                "approved_evidence": [
                    {"id": item.id, "source_ref": item.source_ref, "text": item.text}
                    for item in evidence
                ],
                "external_sync": "not performed",
                "source_modified": False,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return ResumeProposal(
        proposed_tex_path=proposed_tex_path,
        diff_path=diff_path,
        claim_report_path=claim_report_path,
    )


def validate_latex_proposal(
    proposal_path: Path, *, latexmk: Path = Path("latexmk")
) -> LatexValidation:
    """Compile a selected local proposal without touching the resume source or remote."""
    if proposal_path.suffix.lower() != ".tex" or not proposal_path.is_file():
        raise ValueError("proposal_path must point to an existing .tex proposal")
    command = (str(latexmk), "-pdf", "-interaction=nonstopmode", proposal_path.name)
    completed = subprocess.run(
        command,
        cwd=proposal_path.parent,
        capture_output=True,
        check=False,
        text=True,
        timeout=120,
    )
    return LatexValidation(
        command=command,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
