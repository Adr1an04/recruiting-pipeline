from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from recruiting_pipeline.integrations.obsidian_tracker import write_job_tracker_note


class ObsidianTrackerTests(unittest.TestCase):
    def test_creates_reviewable_job_note_with_package_link(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            tracker = root / "tracker"
            tracker.mkdir()
            (tracker / "Fall 2026 Applications.md").write_text(
                "# Fall 2026 Applications\n\n## Application tracker\n\n"
                "| Company | Role | Location / work mode | Source | Status | Applied | "
                "Next action | Contact / link |\n"
                "| --- | --- | --- | --- | --- | --- | --- | --- |\n",
                encoding="utf-8",
            )
            note = write_job_tracker_note(
                tracker_dir=root / "tracker",
                cycle="Fall 2026",
                company="Example Co",
                role="Software Engineer Intern",
                job_url="https://jobs.example.test/123",
                package_dir=root / "applications" / "Fall26" / "ExampleCo",
            )
            self.assertEqual(
                note,
                (
                    tracker / "Fall 2026 Applications" / "Example Co — Software Engineer Intern.md"
                ).resolve(),
            )
            self.assertTrue(note.exists())
            self.assertIn("https://jobs.example.test/123", note.read_text(encoding="utf-8"))
            self.assertIn(
                "[[Example Co — Software Engineer Intern]]",
                (tracker / "Fall 2026 Applications.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                note,
                write_job_tracker_note(
                    tracker_dir=root / "tracker",
                    cycle="Fall 2026",
                    company="Example Co",
                    role="Software Engineer Intern",
                    job_url="https://jobs.example.test/123",
                    package_dir=root / "applications" / "Fall26" / "ExampleCo",
                ),
            )


if __name__ == "__main__":
    unittest.main()
