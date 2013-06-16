import os
import unittest

from php_coverage.config import config
from php_coverage.finder import CoverageFinder


class CoverageFinderTest(unittest.TestCase):

    def setUp(self):
        config.loaded = True
        config.debug = True
        config.report_path = 'foo/bar/baz.xml'
        self.finder = CoverageFinder()
        dir = os.path.join(os.path.dirname(__file__), 'finder')
        self.invalid_src = dir
        self.src = os.path.join(dir, 'src', 'path', 'test.php')
        self.coverage = os.path.join(dir, 'foo', 'bar', 'baz.xml')

    def tearDown(self):
        config.loaded = False
        del config.debug
        del config.report_path

    def test_find(self):
        self.assertEquals(self.finder.find(self.src), self.coverage)

    def test_find_invalid(self):
        self.assertIs(self.finder.find(self.invalid_src), None)
