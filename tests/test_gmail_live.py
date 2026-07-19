from __future__ import annotations

import unittest

from erga_mcp.integrations.gmail_live import (
    fetch_inbox_metadata_with_gws,
    parse_message_metadata,
)


class GmailLiveTests(unittest.TestCase):
    def test_parses_gmail_metadata_without_body_content(self) -> None:
        message = parse_message_metadata(
            {
                "id": "gmail-1",
                "internalDate": "1760000000000",
                "payload": {
                    "headers": [
                        {"name": "From", "value": "recruiter@example.test"},
                        {"name": "Subject", "value": "Software Engineer role"},
                    ]
                },
                "snippet": "Short preview only",
            }
        )

        self.assertEqual(message.message_id, "gmail:gmail-1")
        self.assertEqual(message.sender, "recruiter@example.test")
        self.assertEqual(message.subject, "Software Engineer role")
        self.assertEqual(message.preview, "Short preview only")

    def test_reads_metadata_through_user_configured_gws(self) -> None:
        calls: list[list[str]] = []

        def run(command: list[str]) -> dict[str, object]:
            calls.append(command)
            if "list" in command:
                return {"messages": [{"id": "gmail-1"}]}
            return {
                "id": "gmail-1",
                "internalDate": "1760000000000",
                "payload": {"headers": [{"name": "From", "value": "r@example.test"}]},
            }

        messages = fetch_inbox_metadata_with_gws(gws_command="gws", limit=1, run=run)

        self.assertEqual([item.message_id for item in messages], ["gmail:gmail-1"])
        self.assertEqual(len(calls), 2)
        self.assertIn("list", calls[0])


if __name__ == "__main__":
    unittest.main()
