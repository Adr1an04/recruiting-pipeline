from __future__ import annotations

import unittest
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from recruiting_pipeline.models import Evidence
from recruiting_pipeline.resume import create_section_resume_proposal, replace_section_contents


class ResumeEditorTests(unittest.TestCase):
    def test_replaces_only_the_selected_latex_section_body(self) -> None:
        source = "\\section{Experience}\nold experience\n\\section{Projects}\nold project\n"
        self.assertEqual(
            replace_section_contents(source, "Experience", "new experience"),
            "\\section{Experience}\nnew experience\n\\section{Projects}\nold project\n",
        )

    def test_rejects_missing_or_ambiguous_sections(self) -> None:
        with self.assertRaises(ValueError):
            replace_section_contents("\\section{Projects}\nx\n", "Experience", "new")
        with self.assertRaises(ValueError):
            replace_section_contents(
                "\\section{Experience}\nx\n\\section{Experience}\ny\n", "Experience", "new"
            )

    def test_creates_a_reviewable_section_specific_proposal(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "resume.tex"
            original = "\\section{Experience}\nold\n\\section{Projects}\nkeep\n"
            source.write_text(original, encoding="utf-8")
            evidence = Evidence("ev1", "Career.md#Experience", "verified", True, datetime.now(UTC))
            proposal = create_section_resume_proposal(
                resume_path=source,
                output_dir=root / "proposal",
                section_name="Experience",
                latex_content="new",
                evidence=[evidence],
            )
            self.assertEqual(source.read_text(encoding="utf-8"), original)
            self.assertIn("new", proposal.proposed_tex_path.read_text(encoding="utf-8"))
            self.assertIn("keep", proposal.proposed_tex_path.read_text(encoding="utf-8"))
            self.assertTrue(proposal.diff_path.exists())
            self.assertTrue(proposal.claim_report_path.exists())


if __name__ == "__main__":
    unittest.main()
