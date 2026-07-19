from __future__ import annotations

from pathlib import Path


def _safe_name(value: str) -> str:
    cleaned = "".join(char if char.isalnum() or char in " -_" else "" for char in value).strip()
    if not cleaned or cleaned in {".", ".."}:
        raise ValueError("company and role must contain a safe display name")
    return cleaned


def _upsert_cycle_tracker(
    *, tracker_dir: Path, cycle: str, company: str, role: str, job_url: str, note_name: str
) -> None:
    """Record a job once in its configured cycle tracker, never in a top-level Projects note."""
    cycle_path = tracker_dir / f"{cycle} Applications.md"
    if not cycle_path.is_file():
        raise ValueError(f"cycle tracker does not exist: {cycle_path.name}")
    text = cycle_path.read_text(encoding="utf-8")
    header = (
        "| Company | Role | Location / work mode | Source | Status | Applied | "
        "Next action | Contact / link |"
    )
    divider = "| --- | --- | --- | --- | --- | --- | --- | --- |"
    if header not in text or divider not in text:
        raise ValueError(f"cycle tracker has no application table: {cycle_path.name}")
    marker = f"[[{note_name}]]"
    if marker in text:
        return
    row = (
        f"| {company} | {role} |  | [Posting]({job_url}) | Researching |  | "
        f"Review role requirements and decide whether to apply. | {marker} |"
    )
    text = text.replace(divider, divider + "\n" + row, 1)
    cycle_path.write_text(text, encoding="utf-8")


def write_job_tracker_note(
    *,
    tracker_dir: Path,
    cycle: str,
    company: str,
    role: str,
    job_url: str,
    package_dir: Path,
    resume_pdf: Path | None = None,
) -> Path:
    """Create the detailed note below its cycle and update the cycle tracker."""
    if not job_url.startswith(("https://", "http://")):
        raise ValueError("job URL must use HTTP(S)")
    safe_company, safe_role = _safe_name(company), _safe_name(role)
    notes_dir = tracker_dir.expanduser().resolve()
    notes_dir.mkdir(parents=True, exist_ok=True)
    note_name = f"{safe_company} — {safe_role}"
    cycle_notes_dir = notes_dir / f"{cycle} Applications"
    cycle_notes_dir.mkdir(exist_ok=True)
    note_path = cycle_notes_dir / f"{note_name}.md"
    relative_package = package_dir.expanduser().resolve().as_posix()
    if not note_path.exists():
        pdf_line = f"- Resume PDF: `{resume_pdf.expanduser().resolve()}`\n" if resume_pdf else ""
        note_path.write_text(
            f"# {note_name}\n\n"
            f"- Cycle: [[{cycle} Applications]]\n"
            "- Status: Researching\n"
            f"- Job URL: {job_url}\n"
            f"- Package: `{relative_package}`\n"
            f"{pdf_line}"
            "- Next action: Review tailored résumé and job requirements.\n\n"
            "## Resume / portfolio emphasis\n\n"
            "Generated from approved career evidence; see the package claim report.\n",
            encoding="utf-8",
        )
    _upsert_cycle_tracker(
        tracker_dir=notes_dir,
        cycle=cycle,
        company=safe_company,
        role=safe_role,
        job_url=job_url,
        note_name=note_name,
    )
    return note_path
