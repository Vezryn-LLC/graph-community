"""Run locally; the requested uppercase test deliberately starts red."""
from pathlib import Path
import subprocess
import sys
import unittest

SCRIPT = Path(__file__).with_name("greet.py")


class GreetingTests(unittest.TestCase):
    def greet(self, *args):
        return subprocess.run([sys.executable, "-B", str(SCRIPT), *args],
                              capture_output=True, text=True, timeout=5)

    def test_default(self):
        result = self.greet("Ada")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Hello, Ada!\n")

    def test_uppercase(self):
        result = self.greet("Ada", "--uppercase")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "HELLO, ADA!\n")


if __name__ == "__main__":
    unittest.main()
