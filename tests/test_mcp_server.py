from __future__ import annotations

import asyncio
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from recruiting_pipeline.config import DEFAULT_CONFIG
from recruiting_pipeline.mcp_server import build_server


class McpServerTests(unittest.TestCase):
    def test_exposes_read_and_explicit_local_workspace_tools(self) -> None:
        with TemporaryDirectory() as directory:
            config_path = Path(directory) / "config.toml"
            config_path.write_text(DEFAULT_CONFIG)

            server = build_server(config_path)
            tools = asyncio.run(server.list_tools())

            by_name = {tool.name: tool for tool in tools}
            self.assertEqual(
                set(by_name),
                {
                    "pipeline_status",
                    "list_applications",
                    "list_evidence",
                    "list_mail_events",
                    "prepare_job_workspace",
                    "create_tailored_resume",
                    "validate_tailored_resume",
                },
            )
            for name in {
                "pipeline_status",
                "list_applications",
                "list_evidence",
                "list_mail_events",
            }:
                annotations = by_name[name].annotations
                self.assertIsNotNone(annotations)
                assert annotations is not None
                self.assertTrue(annotations.readOnlyHint)
                self.assertFalse(annotations.openWorldHint)
            workspace_annotations = by_name["prepare_job_workspace"].annotations
            resume_annotations = by_name["create_tailored_resume"].annotations
            validation_annotations = by_name["validate_tailored_resume"].annotations
            assert workspace_annotations is not None
            assert resume_annotations is not None
            assert validation_annotations is not None
            self.assertFalse(workspace_annotations.readOnlyHint)
            self.assertTrue(workspace_annotations.openWorldHint)
            self.assertFalse(resume_annotations.readOnlyHint)
            self.assertFalse(validation_annotations.readOnlyHint)


if __name__ == "__main__":
    unittest.main()
