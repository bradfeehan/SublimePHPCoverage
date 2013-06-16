import unittest

from php_coverage.thread import NullPollingThread
from php_coverage.thread import PollingThread
from php_coverage.thread import Timeout


class NullPollingThreadTest(unittest.TestCase):

    def setUp(self):
        self.thread = NullPollingThread()

    def test_stop(self):
        self.thread.start()
        self.assertTrue(self.thread.is_alive())
        self.thread.stop(0.5)
        self.assertFalse(self.thread.is_alive())

    def test_stop_unsuccessful(self):
        self.thread.start()
        self.assertTrue(self.thread.is_alive())
        with self.assertRaises(Timeout):
            self.thread.stop(0)

    def test_poll_is_abstract(self):
        with self.assertRaises(NotImplementedError):
            PollingThread().poll()
