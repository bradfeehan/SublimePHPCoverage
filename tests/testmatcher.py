import unittest

from php_coverage.config import config
from php_coverage.matcher import Matcher


class MatcherTest(unittest.TestCase):

    def setUp(self):
        config.loaded = True
        # config.debug = True
        config.include = [r"foo.*\.php$", r"win[\\/]do[\\/]ws\.php"]
        config.exclude = [r"foo.*bar\.php$", "foofoo\.php$"]
        self.matcher = Matcher()

    def tearDown(self):
        config.loaded = False
        # del config.debug
        del config.include
        del config.exclude

    def test_should_include(self):
        self.assertTrue(self.matcher.should_include('foo.php'))
        self.assertFalse(self.matcher.should_include('foobar.php'))
        self.assertFalse(self.matcher.should_include('thefoofoo.php'))
        self.assertFalse(self.matcher.should_include('feet.php'))
        self.assertTrue(self.matcher.should_include('win\\do/ws.php'))

    def test_included(self):
        self.assertTrue(self.matcher.included('foo.php'))
        self.assertTrue(self.matcher.included('foobar.php'))
        self.assertTrue(self.matcher.included('thefoofoo.php'))
        self.assertFalse(self.matcher.included('feet.php'))
        self.assertTrue(self.matcher.included('win\\do/ws.php'))

    def test_excluded(self):
        self.assertFalse(self.matcher.excluded('foo.php'))
        self.assertTrue(self.matcher.excluded('foobar.php'))
        self.assertTrue(self.matcher.excluded('thefoofoo.php'))
        self.assertFalse(self.matcher.excluded('feet.php'))
        self.assertFalse(self.matcher.excluded('win\\do/ws.php'))

    def test_match(self):
        patterns = [r"test.+test", r"newtest"]
        self.assertTrue(self.matcher.match(patterns, 'testthistest'))
        self.assertTrue(self.matcher.match(patterns, 'mynewtester'))
        self.assertFalse(self.matcher.match(patterns, 'testtest'))
        self.assertFalse(self.matcher.match(patterns, 'newesttest'))
