import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "onboarding" / "cursor_onboarding.py"
spec = importlib.util.spec_from_file_location("cursor_onboarding", SCRIPT)
assert spec is not None and spec.loader is not None
onboarding = importlib.util.module_from_spec(spec)
spec.loader.exec_module(onboarding)
URL = "https://cursor-bridge.softvibes.cloud/v1/enrich-user-story"


class OnboardingTests(unittest.TestCase):
    def test_url_contract(self):
        self.assertEqual(onboarding.validate_url(URL), URL)
        for bad in (
            "http://cursor-bridge.softvibes.cloud/v1/enrich-user-story",
            "https://user:secret@cursor-bridge.softvibes.cloud/v1/enrich-user-story",
            "https://cursor-bridge.softvibes.cloud/health",
            URL + "?token=secret",
            URL + "#fragment",
            "https://cursor-bridge.softvibes.cloud:broken/v1/enrich-user-story",
            "https://cursor-bridge.softvibes.cloud:0/v1/enrich-user-story",
            "",
        ):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                onboarding.validate_url(bad)

    def test_noninteractive_fails_without_launching_client(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--url", URL, "request.json", "--out", "out.json"],
            stdin=subprocess.DEVNULL, capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("terminal interactiva", result.stderr)
        self.assertNotIn("Token del bridge", result.stderr)

    @patch.object(onboarding.sys.stdin, "isatty", return_value=True)
    @patch.object(onboarding.getpass, "getpass", return_value="test-secret-not-real")
    @patch.object(onboarding.subprocess, "run")
    def test_hidden_token_only_in_child_environment(self, run, prompt, isatty):
        captured = {}

        def record_launch(command, **kwargs):
            captured["command"] = command[:]
            captured["env"] = kwargs["env"].copy()
            return subprocess.CompletedProcess(command, 0)

        run.side_effect = record_launch
        prior = os.environ.get("HERMES_BRIDGE_TOKEN")
        self.assertEqual(onboarding.main(["--url", URL, "request.json", "--out", "out.json"]), 0)
        self.assertEqual(captured["command"][1], str(onboarding.CLIENT))
        self.assertEqual(captured["env"]["HERMES_BRIDGE_TOKEN"], "test-secret-not-real")
        self.assertEqual(captured["env"]["HERMES_BRIDGE_URL"], URL)
        self.assertEqual(os.environ.get("HERMES_BRIDGE_TOKEN"), prior)
        self.assertNotIn("test-secret-not-real", repr(captured["command"]))
        prompt.assert_called_once()

    @patch.object(onboarding.sys.stdin, "isatty", return_value=True)
    @patch.object(onboarding.getpass, "getpass", side_effect=onboarding.getpass.GetPassWarning)
    @patch.object(onboarding.subprocess, "run")
    def test_visible_prompt_fallback_is_rejected(self, run, prompt, isatty):
        self.assertEqual(onboarding.main(["--url", URL, "request.json", "--out", "out.json"]), 2)
        run.assert_not_called()

    @patch.object(onboarding.sys.stdin, "isatty", return_value=True)
    @patch.object(onboarding.getpass, "getpass", return_value="")
    @patch.object(onboarding.subprocess, "run")
    def test_empty_token_does_not_launch_client(self, run, prompt, isatty):
        self.assertEqual(onboarding.main(["--url", URL, "request.json", "--out", "out.json"]), 2)
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
