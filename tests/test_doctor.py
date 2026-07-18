from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from recruiting_pipeline.doctor import check_installation


class DoctorTests(unittest.TestCase):
    def test_core_installation_passes_without_optional_integrations(self) -> None:
        with TemporaryDirectory() as directory:
            config_path = Path(directory) / "config.toml"
            config_path.write_text('[paths]\ndata_dir = "state"\nvault_path = ""\n')

            report = check_installation(config_path)

            self.assertTrue(report.core_ready)
            self.assertIn("config", report.checks)
            self.assertIn("tracker", report.warnings)


if __name__ == "__main__":
    unittest.main()
