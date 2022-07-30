import unittest


class TestParser(unittest.TestCase):
    def setUp(self):
        pass

    def test_basic(self):
        self.assertTrue(True)

    def test_indentation(self):
        self.assertEqual(self.parser.indentation("foobar"), 0)
        self.assertEqual(self.parser.indentation("  foobar"), 2)
        self.assertEqual(self.parser.indentation("    foobar"), 4)
        self.assertEqual(self.parser.indentation("\tfoobar"), 4)
        self.assertEqual(self.parser.indentation("\t\tfoobar"), 8)


if __name__ == "__main__":
    unittest.main()
