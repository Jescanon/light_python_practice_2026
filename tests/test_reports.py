import io
import contextlib
import tempfile
import unittest
from pathlib import Path

from src.service.scaner import scan
from src.service.reports import show_duplicates
from src.database.db import connect

class ReportsTests(unittest.TestCase):

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.db = Path(tempfile.mkdtemp()) / "test.db"

    def make(self, name, text):
        (self.dir / name).write_text(text)

    def do_scan(self):
        with connect(self.db) as conn:
            scan(conn, self.dir)

    def run_duplicates(self):
        out = io.StringIO()
        with connect(self.db) as conn:
            with contextlib.redirect_stdout(out):
                show_duplicates(conn, str(self.dir))
        return out.getvalue()

    def test_finds_duplicate_group(self):
        self.make("a.txt", "same content")
        self.make("b.txt", "same content")
        self.do_scan()
        out = self.run_duplicates()
        self.assertIn("a.txt", out)
        self.assertIn("b.txt", out)

    def test_unique_files_not_reported(self):
        self.make("a.txt", "one")
        self.make("b.txt", "two")
        self.do_scan()
        out = self.run_duplicates()
        self.assertNotIn("a.txt", out)
        self.assertNotIn("b.txt", out)

    def test_empty_db_message(self):
        out = self.run_duplicates()
        self.assertIn("Не найдено", out)


if __name__ == "__main__":
    unittest.main()
