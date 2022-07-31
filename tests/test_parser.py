import unittest
from pathlib import Path
from unittest import mock

from org2anki.orgparse import OrgParser


class TestParser(unittest.TestCase):
    def setUp(self):
        self.org_path = Path.cwd() / "sample" / "org"
        self.parser = OrgParser("~")

    def test_basic(self):
        self.assertTrue(True)

    def test_indentation(self):
        self.assertEqual(self.parser._indentation("foobar"), 0)
        self.assertEqual(self.parser._indentation("  foobar"), 2)
        self.assertEqual(self.parser._indentation("    foobar"), 4)
        self.assertEqual(self.parser._indentation("\tfoobar"), 2)
        self.assertEqual(self.parser._indentation("\t\tfoobar"), 4)

    @mock.patch("shutil.copy")
    def test_copy_image_to_anki_media_dir(self, mock_shutil_copy):
        img_path = str((self.org_path / "sample1.org").resolve())
        enc_img_path = img_path.encode().hex() + ".o2a"
        self.assertEqual(
            self.parser._copy_image_to_anki_media_dir(img_path),
            f'<img src=""{enc_img_path}"" />',
        )


if __name__ == "__main__":
    unittest.main()
