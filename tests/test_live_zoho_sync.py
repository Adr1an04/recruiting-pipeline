from __future__ import annotations

import unittest
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from erga_mcp.integrations.zoho import MailMessageMetadata
from erga_mcp.integrations.zoho_live import format_recruiting_alerts, sync_metadata
from erga_mcp.store import ErgaStore


class LiveZohoSyncTests(unittest.TestCase):
    def test_records_new_messages_once_with_application_job_and_other_categories(self) -> None:
        messages = [
            MailMessageMetadata(
                "m1",
                datetime(2026, 7, 18, tzinfo=UTC),
                "jobs@example.com",
                "Application received",
                "Thanks for applying",
            ),
            MailMessageMetadata(
                "m2",
                datetime(2026, 7, 18, tzinfo=UTC),
                "recruiter@example.com",
                "Software Engineer role",
                "I found your profile and would like to connect",
            ),
            MailMessageMetadata(
                "m3",
                datetime(2026, 7, 18, tzinfo=UTC),
                "news@example.com",
                "July newsletter",
                "Read our latest news",
            ),
        ]
        with TemporaryDirectory() as directory:
            store = ErgaStore(Path(directory) / "erga.sqlite3")
            self.assertEqual(
                sync_metadata(store, messages),
                {
                    "application": 1,
                    "job": 1,
                    "other": 1,
                    "created": 3,
                    "alerts": [
                        {
                            "kind": "application.acknowledgement",
                            "received_at": "2026-07-18T00:00:00+00:00",
                            "sender": "jobs@example.com",
                            "subject": "Application received",
                            "requires_review": False,
                        },
                        {
                            "kind": "job.candidate",
                            "received_at": "2026-07-18T00:00:00+00:00",
                            "sender": "recruiter@example.com",
                            "subject": "Software Engineer role",
                            "requires_review": True,
                        },
                    ],
                },
            )
            self.assertEqual(sync_metadata(store, messages)["created"], 0)
            self.assertEqual(sync_metadata(store, messages)["alerts"], [])

    def test_renders_only_new_relevant_mail_with_source_and_subject(self) -> None:
        message = MailMessageMetadata(
            "m1",
            datetime(2026, 7, 18, tzinfo=UTC),
            "recruiting@acme.example",
            "Online assessment invitation",
            "Complete the coding test.",
        )
        with TemporaryDirectory() as directory:
            summary = sync_metadata(ErgaStore(Path(directory) / "erga.sqlite3"), [message])

        self.assertEqual(
            summary["alerts"],
            [
                {
                    "kind": "application.assessment",
                    "received_at": "2026-07-18T00:00:00+00:00",
                    "sender": "recruiting@acme.example",
                    "subject": "Online assessment invitation",
                    "requires_review": True,
                }
            ],
        )
        self.assertEqual(
            format_recruiting_alerts(summary["alerts"]),
            "📬 Recruiting inbox update\n\n"
            "Assessment invitation — needs review\n"
            "Received: 2026-07-18T00:00:00+00:00\n"
            "From: recruiting@acme.example\n"
            "Subject: Online assessment invitation",
        )


if __name__ == "__main__":
    unittest.main()
