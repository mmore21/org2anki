import unittest
from pathlib import Path

from org2anki.converter import Converter


class TestConverter(unittest.TestCase):
    def setUp(self):
        self.org_path = Path.cwd() / "sample" / "org"
        self.anki_path = Path.cwd() / "sample" / "anki"
        self.converter = Converter(
            self.org_path, self.anki_path, recursive=False, verbose=False
        )

    def test_get_anki_export_path(self):
        org_file_path = self.org_path / "sample1.org"
        anki_file_path = self.anki_path / "sample1"
        self.assertEqual(
            self.converter._get_anki_export_path(org_file_path), anki_file_path
        )

    def test_is_org_mode_file(self):
        org_file_path = self.org_path / "sample1.org"
        self.assertTrue(self.converter._is_org_mode_file(org_file_path))
