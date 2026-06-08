import io
import contextlib
import tempfile
import unittest
from pathlib import Path

from src.service.compare import comparing
from src.database.db import connect

class CompareTests(unittest.TestCase):

    def setUp(self):
        self.src = Path(tempfile.mkdtemp())
        self.bak = Path(tempfile.mkdtemp())
        self.db = Path(tempfile.mkdtemp()) / "test.db"

    def make(self, base, name, text):
        (base / name).write_text(text)

    def run_compare(self):
        out = io.StringIO()
        with connect(self.db) as conn:
            with contextlib.redirect_stdout(out):
                comparing(conn, str(self.src), str(self.bak))
        return out.getvalue()

    def last_check(self):
        with connect(self.db) as conn:
            return conn.execute(
                "SELECT missing, changed, extra FROM checks ORDER BY id DESC LIMIT 1"
            ).fetchone()

    def test_identical_no_diff(self):
        self.make(self.src, "a.txt", "same")
        self.make(self.bak, "a.txt", "same")
        out = self.run_compare()
        self.assertIn("присутствует", out.lower())

    def test_missing_in_backup(self):
        self.make(self.src, "only.txt", "x")
        out = self.run_compare()
        self.assertIn("only.txt", out)

    def test_extra_in_backup(self):
        self.make(self.bak, "junk.txt", "x")
        out = self.run_compare()
        self.assertIn("junk.txt", out)

    def test_changed_content(self):
        self.make(self.src, "a.txt", "one")
        self.make(self.bak, "a.txt", "two")
        out = self.run_compare()
        self.assertIn("a.txt", out)

    def test_check_saved_counts(self):
        self.make(self.src, "only.txt", "x")
        self.make(self.src, "ch.txt", "v1"); self.make(self.bak, "ch.txt", "v2")
        self.make(self.bak, "e1.txt", "y"); self.make(self.bak, "e2.txt", "z")
        self.run_compare()
        row = self.last_check()
        self.assertEqual(row["missing"], 1)
        self.assertEqual(row["changed"], 1)
        self.assertEqual(row["extra"], 2)


if __name__ == "__main__":
    unittest.main()
