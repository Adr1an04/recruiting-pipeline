from __future__ import annotations

import json
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from erga_mcp.cli import main


class CliWorkflowTests(unittest.TestCase):
    def _run(self, arguments: list[str]) -> tuple[int, dict[str, object]]:
        output = StringIO()
        with redirect_stdout(output):
            exit_code = main(arguments)
        return exit_code, json.loads(output.getvalue())

    def test_can_capture_approved_evidence_and_create_a_draft_application(self) -> None:
        with TemporaryDirectory() as directory:
            config_path = Path(directory) / "config.toml"
            main(["init", "--config", str(config_path)])

            evidence_code, evidence = self._run(
                [
                    "evidence",
                    "add",
                    "--config",
                    str(config_path),
                    "--source-ref",
                    "Career/Projects.md#Pipeline",
                    "--text",
                    "Reduced manual review time using a measured workflow.",
                    "--approved",
                ]
            )
            application_code, application = self._run(
                [
                    "applications",
                    "add",
                    "--config",
                    str(config_path),
                    "--company",
                    "Example Systems",
                    "--role",
                    "Software Engineer",
                    "--source-url",
                    "https://jobs.example.test/123",
                    "--evidence-id",
                    str(evidence["id"]),
                ]
            )

            self.assertEqual(evidence_code, 0)
            self.assertTrue(evidence["approved"])
            self.assertEqual(application_code, 0)
            self.assertEqual(application["status"], "draft")
            self.assertEqual(application["evidence_ids"], [evidence["id"]])

            status_code, updated = self._run(
                [
                    "applications",
                    "update-status",
                    "--config",
                    str(config_path),
                    "--application-id",
                    str(application["id"]),
                    "--status",
                    "applied",
                ]
            )

            self.assertEqual(status_code, 0)
            self.assertEqual(updated["status"], "applied")

            archive = Path(directory) / "exports" / "pipeline.zip"
            export_code, exported = self._run(
                ["export", "--config", str(config_path), "--output", str(archive)]
            )
            self.assertEqual(export_code, 0)
            self.assertEqual(exported["applications"], 1)
            self.assertTrue(archive.is_file())


if __name__ == "__main__":
    unittest.main()
