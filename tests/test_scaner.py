import tempfile
import unittest
from pathlib import Path

from src.service.scaner import _parse_ext, walk, scan
from src.database.db import connect

class ScanerTests(unittest.TestCase):

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.db = Path(tempfile.mkdtemp()) / "test.db"

    def make_files(self, *names):
        for n in names:
            (self.dir / n).write_text("x")

    def count(self):
        with connect(self.db) as conn:
            return conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]

    def test_parse_ext_adds_dot(self):
        self.assertEqual(_parse_ext("py"), {".py"})

    def test_parse_ext_empty(self):
        self.assertIsNone(_parse_ext(""))

    def test_walk_finds_files(self):
        self.make_files("a.py", "b.txt")
        rows = []
        walk(self.dir, self.dir, rows)
        self.assertEqual(len(rows), 2)

    def test_walk_skips_venv(self):
        self.make_files("a.py")
        venv = self.dir / "venv"
        venv.mkdir()
        (venv / "junk.py").write_text("x")
        rows = []
        walk(self.dir, self.dir, rows)
        self.assertEqual(len(rows), 1)

    def test_scan_saves_files(self):
        self.make_files("a.py", "b.py", "c.txt")
        with connect(self.db) as conn:
            scan(conn, self.dir)
        self.assertEqual(self.count(), 3)

    def test_scan_ext_filter(self):
        self.make_files("a.py", "b.py", "c.txt")
        with connect(self.db) as conn:
            scan(conn, self.dir, ext=".py")
        self.assertEqual(self.count(), 2)

    def test_scan_twice_no_duplicate(self):
        self.make_files("a.py")
        with connect(self.db) as conn:
            scan(conn, self.dir)
        with connect(self.db) as conn:
            scan(conn, self.dir)
        self.assertEqual(self.count(), 1)


if __name__ == "__main__":
    unittest.main()
