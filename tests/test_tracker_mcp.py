from __future__ import annotations

import asyncio
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, cast

from erga_mcp.config import DEFAULT_CONFIG
from erga_mcp.mcp_server import build_server


class TrackerMcpTests(unittest.TestCase):
    def test_returns_a_rendered_obsidian_tracker_without_writing_the_vault(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            tracker = root / "tracker"
            tracker.mkdir()
            tracker_path = tracker / "Fall 2026 Application Tracker.md"
            original = (
                "| Company | Role | Location / work mode | Source | Status | Applied | "
                "Next action | Contact / link |\n"
                "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
                "| Example Co | Software Engineer Intern | Remote | Source | Applied | "
                "2026-07-20 | Await update | Note |\n"
            )
            tracker_path.write_text(original, encoding="utf-8")
            config_path = root / "config.toml"
            config_path.write_text(
                DEFAULT_CONFIG.replace(
                    'enabled = false\ntracker_dir = ""',
                    'enabled = true\ntracker_dir = "tracker"',
                ),
                encoding="utf-8",
            )

            result: Any = asyncio.run(
                build_server(config_path).call_tool("application_tracker", {})
            )
            payload = cast(dict[str, Any], result[1])

            self.assertEqual(payload["summary"], {"applied": 1})
            self.assertIn("Erga application tracker", payload["message"])
            self.assertIn("Example Co", payload["message"])
            self.assertEqual(tracker_path.read_text(encoding="utf-8"), original)

    def test_reports_disabled_tracking_without_reading_a_vault(self) -> None:
        with TemporaryDirectory() as directory:
            config_path = Path(directory) / "config.toml"
            config_path.write_text(DEFAULT_CONFIG, encoding="utf-8")

            result: Any = asyncio.run(
                build_server(config_path).call_tool("application_tracker", {})
            )
            payload = cast(dict[str, Any], result[1])

        self.assertFalse(payload["enabled"])
        self.assertIn("not configured", payload["message"])


if __name__ == "__main__":
    unittest.main()
