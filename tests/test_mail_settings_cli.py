from __future__ import annotations

import json
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from erga_mcp.cli import main
from erga_mcp.config import load_config


class MailSettingsCliTests(unittest.TestCase):
    def test_configures_non_secret_scheduled_mail_settings(self) -> None:
        with TemporaryDirectory() as directory:
            config = Path(directory) / "config.toml"
            main(["init", "--config", str(config)])
            output = StringIO()

            with redirect_stdout(output):
                self.assertEqual(
                    main(
                        [
                            "mail",
                            "configure",
                            "--config",
                            str(config),
                            "--provider",
                            "zoho",
                            "--client-id",
                            "synthetic-client",
                            "--accounts-url",
                            "https://accounts.zoho.eu",
                        ]
                    ),
                    0,
                )

            result = json.loads(output.getvalue())
            loaded = load_config(config)
            self.assertEqual(result["client_id"], "synthetic-client")
            self.assertEqual(loaded.mail_client_id, "synthetic-client")
            rendered = config.read_text(encoding="utf-8").casefold()
            self.assertNotIn("client_secret", rendered)
            self.assertNotIn("access_token", rendered)

            repeated_output = StringIO()
            with redirect_stdout(repeated_output):
                self.assertEqual(
                    main(
                        [
                            "mail",
                            "configure",
                            "--config",
                            str(config),
                            "--provider",
                            "zoho",
                            "--client-id",
                            "synthetic-client",
                            "--accounts-url",
                            "https://accounts.zoho.eu",
                        ]
                    ),
                    0,
                )
            self.assertEqual(
                json.loads(repeated_output.getvalue())["client_id"],
                "synthetic-client",
            )


if __name__ == "__main__":
    unittest.main()
