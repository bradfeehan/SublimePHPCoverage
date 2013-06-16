import os
import unittest
import xml.etree.ElementTree

from php_coverage.data import CoverageData
from php_coverage.data import FileCoverage


class CoverageDataTest(unittest.TestCase):

    def setUp(self):
        file = os.path.join(os.path.dirname(__file__), 'data', 'test.xml')
        self.data = CoverageData(file)

    def test_is_loaded(self):
        self.assertFalse(self.data.is_loaded())
        self.data.elements = []
        self.assertTrue(self.data.is_loaded())

    def test_load(self):
        self.data.load()
        self.assertTrue(self.data.is_loaded())
        self.assertEquals(self.data.files, {})

    def test_load_nonexistent_file(self):
        self.data = CoverageData('/path/to/nonexistent/coverage.xml')
        self.data.load()
        self.assertTrue(self.data.is_loaded())
        self.assertEquals(self.data.elements, [])
        self.assertEquals(self.data.files, {})

    def test_normalise(self):
        out = self.data.normalise('/path/to/../the/../../file')
        self.assertEquals(out, '/file')

    def test_get_file(self):
        self.data.load()
        coverage = self.data.get_file('/path/to/file.php')
        self.assertIsInstance(coverage, FileCoverage)

    def test_get_file_implicit_load(self):
        coverage = self.data.get_file('/path/to/file.php')
        self.assertIsInstance(coverage, FileCoverage)

    def test_get_file_invalid(self):
        self.data.load()
        coverage = self.data.get_file('/path/to/nonexistent/file.php')
        self.assertIs(coverage, None)


class FileCoverageTest(unittest.TestCase):

    def setUp(self):
        file = os.path.join(os.path.dirname(__file__), 'data', 'test.xml')
        tree = xml.etree.ElementTree.parse(file)
        element = tree.findall('./project//file')[0]
        self.coverage = FileCoverage('/path/to/file.php', element)

    def test_is_parsed(self):
        self.assertFalse(self.coverage.is_parsed())
        self.coverage.parse()
        self.assertTrue(self.coverage.is_parsed())

    def test_parse(self):
        self.coverage.parse()
        self.assertEquals(self.coverage.num_lines, 16)
        self.assertEquals(self.coverage.covered, 0)
        self.assertEquals(self.coverage.statements, 4)
        self.assertEquals(self.coverage.good_lines, [])
        self.assertEquals(self.coverage.bad_lines, [12, 13, 14, 15])

    def test_get_implicit_parse(self):
        self.assertEquals(self.coverage.num_lines, 16)

if __name__ == '__main__':
    unittest.main()
