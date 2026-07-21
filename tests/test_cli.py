from __future__ import annotations

import json
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from erga_mcp.cli import main
from erga_mcp.config import load_config
from erga_mcp.store import ErgaStore


class CliTests(unittest.TestCase):
    def test_init_creates_a_non_secret_config_and_local_database(self) -> None:
        with TemporaryDirectory() as directory:
            config_path = Path(directory) / "config" / "config.toml"

            exit_code = main(["init", "--config", str(config_path)])

            config = load_config(config_path)
            self.assertEqual(exit_code, 0)
            self.assertTrue(config_path.exists())
            self.assertTrue((config.data_dir / "erga.sqlite3").exists())
            self.assertNotIn("token", config_path.read_text().lower())

    def test_status_includes_mail_event_count(self) -> None:
        with TemporaryDirectory() as directory:
            config_path = Path(directory) / "config.toml"
            main(["init", "--config", str(config_path)])
            output = StringIO()

            with redirect_stdout(output):
                exit_code = main(["status", "--config", str(config_path)])

            self.assertEqual(exit_code, 0)
            self.assertEqual(json.loads(output.getvalue())["mail_events"], 0)

    def test_tokens_command_reports_input_output_and_total_for_one_application(self) -> None:
        with TemporaryDirectory() as directory:
            config_path = Path(directory) / "config.toml"
            main(["init", "--config", str(config_path)])
            application_output = StringIO()
            with redirect_stdout(application_output):
                main(
                    [
                        "applications",
                        "add",
                        "--config",
                        str(config_path),
                        "--company",
                        "Example",
                        "--role",
                        "Engineer",
                        "--source-url",
                        "https://jobs.example.test/123",
                    ]
                )
            application_id = json.loads(application_output.getvalue())["id"]
            store = ErgaStore(load_config(config_path).data_dir / "erga.sqlite3")
            store.record_token_usage(
                application_id=application_id,
                operation="intake",
                input_tokens=700,
                output_tokens=123,
            )
            output = StringIO()

            with redirect_stdout(output):
                exit_code = main(
                    ["tokens", "--config", str(config_path), "--application-id", application_id]
                )

            self.assertEqual(exit_code, 0)
            self.assertEqual(
                json.loads(output.getvalue()),
                {
                    "applications": 1,
                    "events": 1,
                    "input_tokens": 700,
                    "output_tokens": 123,
                    "total_tokens": 823,
                },
            )


if __name__ == "__main__":
    unittest.main()
