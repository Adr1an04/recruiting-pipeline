from __future__ import annotations

import json
import unittest
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from erga_mcp.models import Evidence
from erga_mcp.resume_tailoring import (
    _relevance,
    create_automatic_resume_proposal,
    pdf_page_count,
)

_TEMPLATE = r"""
\documentclass{article}
\begin{document}
\section{Experience}
\resumeSubHeadingListStart
\resumeSubheading{Engineer}{2026}{Example}{Remote}
\resumeItemListStart
\resumeItem{Created visual website content and marketing pages for a student organization.}
\resumeItem{Built Python real-time APIs with FastAPI and Docker for low-latency services.}
\resumeItemListEnd
\resumeSubHeadingListEnd
\section{Projects}
\resumeSubHeadingListStart
\resumeProjectHeading{\textbf{Design Site} $|$ \textit{JavaScript, React}}{}
\resumeItemListStart
\resumeItem{Designed a responsive website and reusable visual content system.}
\resumeItemListEnd
\resumeProjectHeading{\textbf{Stream Engine} $|$ \textit{Python, PyTorch, Docker}}{}
\resumeItemListStart
\resumeItem{Implemented a real-time inference engine with low-latency Python services.}
\resumeItemListEnd
\resumeSubHeadingListEnd
\section{Technical Skills}
\textbf{Languages:} JavaScript, Python \\
\textbf{Frameworks:} React, FastAPI \\
\textbf{Libraries:} Pandas, PyTorch \\
\textbf{Tools / Platforms:} Figma, Docker \\
\end{document}
""".lstrip()


class AutomaticResumeTailoringTests(unittest.TestCase):
    def test_relevance_requires_term_boundaries_and_rejects_substring_collisions(self) -> None:
        for skill, unrelated in (
            ("Java", "JavaScript"),
            ("Rust", "high-trust collaborator"),
            ("AWS", "applicable laws"),
            ("Express", "preference expressed"),
            ("scikit-learn", "drive to learn"),
        ):
            score, matched = _relevance(skill, unrelated)
            self.assertEqual((score, matched), (0, ()), (skill, unrelated))

        self.assertGreater(_relevance("Java", "Production Java services")[0], 0)
        self.assertGreater(_relevance("AWS", "Deploy on AWS")[0], 0)

    def test_embedded_hardware_signals_outweigh_generic_test_vocabulary(self) -> None:
        role = "Embedded software test engineer using MCU, DSP, C++, Python, and test automation"
        embedded = _relevance("C++ sensor pipeline with Arduino, IMU, and EMG hardware", role)[0]
        generic_testing = _relevance("Python Pytest regression tests for CLI parsing", role)[0]
        self.assertGreater(embedded, generic_testing)

    def test_reorders_existing_experience_projects_and_every_skill_category(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "resume.tex"
            source.write_text(_TEMPLATE, encoding="utf-8")
            evidence = Evidence(
                id="ev_python",
                source_ref="Career.md#API",
                text=(
                    "Built Python real-time APIs with FastAPI and Docker for low-latency services."
                ),
                approved=True,
                created_at=datetime.now(UTC),
            )

            result = create_automatic_resume_proposal(
                resume_path=source,
                output_dir=root / "artifacts",
                job_description=(
                    "Python real-time low-latency inference with FastAPI, PyTorch, and Docker"
                ),
                evidence=[evidence],
                editable_sections=("experience", "projects", "technical-skills"),
            )

            proposed = result.proposal.proposed_tex_path.read_text(encoding="utf-8")
            self.assertTrue(result.meaningful_change)
            self.assertEqual(
                result.changed_sections,
                ("Experience", "Projects", "Technical Skills"),
            )
            self.assertLess(proposed.index("Built Python"), proposed.index("Created visual"))
            self.assertLess(proposed.index("Stream Engine"), proposed.index("Design Site"))
            for expected in (
                r"\textbf{Languages:} Python, JavaScript",
                r"\textbf{Frameworks:} FastAPI, React",
                r"\textbf{Libraries:} PyTorch, Pandas",
                r"\textbf{Tools / Platforms:} Docker, Figma",
            ):
                self.assertIn(expected, proposed)

            report = json.loads(result.proposal.claim_report_path.read_text(encoding="utf-8"))
            python_claim = next(
                claim for claim in report["claims"] if claim["text"].startswith("Built Python")
            )
            self.assertEqual(python_claim["evidence_ids"], ["ev_python"])
            self.assertEqual(python_claim["source_kind"], "approved_evidence")
            self.assertFalse(python_claim["text_changed"])
            self.assertEqual(len(report["skills"]), 8)
            self.assertGreater(result.proposal.diff_path.stat().st_size, 0)
            self.assertEqual(source.read_text(encoding="utf-8"), _TEMPLATE)

    def test_uses_an_explicit_baseline_only_when_no_relevant_ordering_change_exists(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "resume.tex"
            source.write_text(_TEMPLATE, encoding="utf-8")

            result = create_automatic_resume_proposal(
                resume_path=source,
                output_dir=root / "artifacts",
                job_description="unrelated quasar geology",
                evidence=[],
                editable_sections=("experience", "projects", "technical-skills"),
            )

            self.assertFalse(result.meaningful_change)
            self.assertEqual(result.proposal.diff_path.read_text(encoding="utf-8"), "")
            report = json.loads(result.proposal.claim_report_path.read_text(encoding="utf-8"))
            self.assertTrue(report["tailoring"]["baseline_fallback"])
            self.assertIn("No meaningful", report["tailoring"]["reason"])

    def test_length_constraints_report_legacy_outliers_without_blocking_safe_reordering(
        self,
    ) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "resume.tex"
            source.write_text(_TEMPLATE, encoding="utf-8")

            result = create_automatic_resume_proposal(
                resume_path=source,
                output_dir=root / "artifacts",
                job_description="Python FastAPI Docker",
                evidence=[],
                editable_sections=("experience",),
                bullet_min_chars=99,
                bullet_target_chars=105,
                bullet_max_chars=116,
            )

            report = json.loads(result.proposal.claim_report_path.read_text(encoding="utf-8"))
            lengths = report["constraints"]["bullet_characters"]
            self.assertTrue(lengths["passed"])
            self.assertGreater(len(lengths["legacy_violations"]), 0)
            self.assertEqual(lengths["new_violations"], [])
            self.assertEqual(result.constraint_violations, ())

    def test_pdf_page_count_is_portable_and_counts_only_page_objects(self) -> None:
        with TemporaryDirectory() as directory:
            pdf = Path(directory) / "resume.pdf"
            pdf.write_bytes(
                b"%PDF-1.4\n1 0 obj<</Type /Pages /Count 2>>endobj\n"
                b"2 0 obj<</Type /Page>>endobj\n3 0 obj<</Type /Page >>endobj\n%%EOF"
            )
            self.assertEqual(pdf_page_count(pdf), 2)


if __name__ == "__main__":
    unittest.main()
