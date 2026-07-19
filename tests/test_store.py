from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from erga_mcp.store import ErgaStore


class StoreTests(unittest.TestCase):
    def test_records_evidence_and_application_with_audit_trail(self) -> None:
        with TemporaryDirectory() as directory:
            store = ErgaStore(Path(directory) / "erga.sqlite3")
            store.initialize()

            evidence = store.add_evidence(
                source_ref="Career/Projects.md#Pipeline",
                text="Reduced manual review time by a measured amount.",
                approved=True,
            )
            application = store.create_application(
                company="Example Systems",
                role="Software Engineer",
                source_url="https://jobs.example.test/123",
                evidence_ids=[evidence.id],
            )

            self.assertEqual(application.status, "draft")
            self.assertEqual(application.evidence_ids, [evidence.id])
            self.assertEqual(store.list_applications(), [application])
            self.assertEqual(store.audit_events()[0].action, "application.created")

            updated = store.update_application_metadata(
                application.id,
                company="Correct Example Systems",
                role="Software Engineering Intern",
            )
            self.assertEqual(updated.company, "Correct Example Systems")
            self.assertEqual(updated.role, "Software Engineering Intern")
            self.assertEqual(updated.status, application.status)
            self.assertEqual(updated.evidence_ids, application.evidence_ids)
            audit_count = len(store.audit_events())
            self.assertEqual(store.audit_events()[0].action, "application.metadata_updated")
            store.update_application_metadata(
                application.id,
                company="Correct Example Systems",
                role="Software Engineering Intern",
            )
            self.assertEqual(len(store.audit_events()), audit_count)

            status = store.update_application_status(application.id, status="interview")
            self.assertEqual(status.status, "interview")
            status_audit = store.audit_events()[0]
            self.assertEqual(status_audit.action, "application.status_updated")
            self.assertEqual(status_audit.payload, {"from": "draft", "to": "interview"})

            with self.assertRaisesRegex(ValueError, "status must be one of"):
                store.update_application_status(application.id, status="submitted magically")


if __name__ == "__main__":
    unittest.main()
