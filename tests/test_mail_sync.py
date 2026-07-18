from __future__ import annotations

import unittest
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from recruiting_pipeline.cli import main
from recruiting_pipeline.integrations.zoho import MailMessageMetadata


class MailSyncTests(unittest.TestCase):
    def test_mail_sync_dispatches_gmail_provider(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "config.toml"
            config.write_text('[paths]\ndata_dir = "state"\n[mail]\nprovider = "gmail"\n')
            message = MailMessageMetadata(
                message_id="gmail:one",
                received_at=datetime(2026, 1, 1, tzinfo=UTC),
                sender="recruiter@example.test",
                subject="Application received",
                preview="Thanks for applying",
            )
            with patch(
                "recruiting_pipeline.cli.fetch_inbox_metadata_with_gws", return_value=[message]
            ):
                self.assertEqual(main(["mail", "sync", "--config", str(config)]), 0)


if __name__ == "__main__":
    unittest.main()
