"""The tutorial runs in a disposable local copy without accounts or Graph."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class FirstIssueTests(unittest.TestCase):
    def test_baseline_and_deliberately_missing_acceptance(self):
        with tempfile.TemporaryDirectory(prefix="First issue spaces ") as folder:
            fixture = Path(folder) / "fixture"
            shutil.copytree(ROOT / "examples/first-issue", fixture)
            def run(*args):
                return subprocess.run([sys.executable, "-B", *args], cwd=fixture,
                                      capture_output=True, text=True, timeout=5)
            greeting = run("greet.py", "Ada")
            self.assertEqual(greeting.returncode, 0, greeting.stderr)
            self.assertEqual(greeting.stdout, "Hello, Ada!\n")
            baseline = run("-m", "unittest", "-v", "test_greet.GreetingTests.test_default")
            self.assertEqual(baseline.returncode, 0, baseline.stderr)
            acceptance = run("-m", "unittest", "-v", "test_greet.GreetingTests.test_uppercase")
            self.assertEqual(acceptance.returncode, 1, acceptance.stderr)
            self.assertIn("unrecognized arguments: --uppercase", acceptance.stderr)
            self.assertEqual(sorted(p.name for p in fixture.iterdir()),
                             ["ISSUE.md", "README.md", "greet.py", "test_greet.py"])


if __name__ == "__main__":
    unittest.main()
