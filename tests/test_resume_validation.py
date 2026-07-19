from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from erga_mcp.resume import resolve_latexmk_executable, validate_latex_proposal


class ResumeValidationTests(unittest.TestCase):
    def test_compiles_only_a_proposed_tex_file_with_a_user_selected_latexmk(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            proposal = root / "proposal.tex"
            proposal.write_text("\\begin{document}ok\\end{document}\n", encoding="utf-8")
            latexmk = root / "fake-latexmk"
            latexmk.write_text("#!/bin/sh\nprintf 'validated %s\\n' \"$*\"\n", encoding="utf-8")
            latexmk.chmod(0o755)

            result = validate_latex_proposal(proposal, latexmk=latexmk)

            self.assertEqual(result.returncode, 0)
            self.assertIn("proposal.tex", result.stdout)
            self.assertEqual(
                proposal.read_text(encoding="utf-8"), "\\begin{document}ok\\end{document}\n"
            )

    def test_resolves_mactex_when_launchd_path_omits_texbin(self) -> None:
        with TemporaryDirectory() as directory:
            texbin = Path(directory)
            latexmk = texbin / "latexmk"
            latexmk.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            latexmk.chmod(0o755)

            with (
                patch("erga_mcp.resume.sys.platform", "darwin"),
                patch("erga_mcp.resume.shutil.which", return_value=None),
                patch("erga_mcp.resume._MACOS_TEXBIN", texbin),
            ):
                resolved = resolve_latexmk_executable(Path("latexmk"))

            self.assertEqual(resolved, latexmk)

    def test_adds_compiler_directory_to_child_path(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            proposal = root / "proposal.tex"
            proposal.write_text("\\begin{document}ok\\end{document}\n", encoding="utf-8")
            latexmk = root / "fake-latexmk"
            latexmk.write_text('#!/bin/sh\nfake-tex-engine "$@"\n', encoding="utf-8")
            latexmk.chmod(0o755)
            engine = root / "fake-tex-engine"
            engine.write_text("#!/bin/sh\nprintf 'child engine found\\n'\n", encoding="utf-8")
            engine.chmod(0o755)

            with patch.dict("os.environ", {"PATH": "/usr/bin:/bin"}, clear=False):
                result = validate_latex_proposal(proposal, latexmk=latexmk)

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "child engine found\n")


if __name__ == "__main__":
    unittest.main()
