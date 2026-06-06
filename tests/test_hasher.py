import tempfile
import unittest
from pathlib import Path

from src.service.hasher import file_hash

class HasherTests(unittest.TestCase):

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())

    def make(self, name, text):
        path = self.dir / name
        path.write_text(text)
        return path

    def test_same_content_same_hash(self):
        a = self.make("a.txt", "hello world")
        b = self.make("b.txt", "hello world")
        self.assertEqual(file_hash(a), file_hash(b))

    def test_different_content_different_hash(self):
        a = self.make("a.txt", "hello world")
        b = self.make("b.txt", "other content")
        self.assertNotEqual(file_hash(a), file_hash(b))

    def test_hash_is_hex_string(self):
        a = self.make("a.txt", "x")
        h = file_hash(a)
        self.assertIsInstance(h, str)
        int(h, 16)


if __name__ == "__main__":
    unittest.main()
