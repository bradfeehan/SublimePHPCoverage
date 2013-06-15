import os
import threading
import unittest

from php_coverage.watcher import CoverageWatcher, FileWatcher
from unittest.mock import Mock, MagicMock

CREATED = FileWatcher.CREATED
DELETED = FileWatcher.DELETED
MODIFIED = FileWatcher.MODIFIED
UNCHANGED = FileWatcher.UNCHANGED


class TestFileWatcher(unittest.TestCase):

    def setUp(self):
        dir = os.path.join(os.path.dirname(__file__), 'watcher')
        if not os.path.exists(dir):
            os.mkdir(dir)
        self.file = os.path.join(dir, 'test.txt')
        self.watcher = FileWatcher(self.file)
        self.detected = threading.Event()
        self.delete()

    def tearDown(self):
        if self.watcher.is_alive():
            self.watcher.stop(1)

        assert(not self.watcher.is_alive())

    def test_created(self):
        self.watcher.add_callback(CREATED, 1, lambda: self.detected.set())
        self.watcher.start()
        self.create('created')
        self.assertTrue(self.detected.wait(1))

    def test_deleted(self):
        self.watcher.add_callback(DELETED, 1, lambda: self.detected.set())
        self.create('deleted')
        self.watcher.start()
        self.delete()
        self.assertTrue(self.detected.wait(1))

    def test_modified(self):
        self.watcher.add_callback(MODIFIED, 1, lambda: self.detected.set())
        self.create('modified1')
        self.watcher.start()
        self.modify('modified2')
        self.assertTrue(self.detected.wait(1))

    def test_unchanged(self):
        self.watcher.add_callback(UNCHANGED, 1, lambda: self.detected.set())
        self.create('unchanged')
        self.watcher.start()
        self.modify('unchanged')
        self.assertTrue(self.detected.wait(1))

    def create(self, content, mode='x'):
        if not os.path.exists(os.path.dirname(self.file)):
            os.mkdir(os.path.dirname(self.file))

        with open(self.file, mode) as file:
            file.write(content)

    def modify(self, content):
        self.create(content, 'w')

        # bump mtime 10s into the future
        new_atime = os.path.getatime(self.file) + 10
        new_mtime = os.path.getmtime(self.file) + 10
        os.utime(self.file, (new_atime, new_mtime))

    def delete(self):
        if os.path.exists(self.file):
            os.remove(self.file)


class TestCoverageWatcher(TestFileWatcher):

    def setUp(self):
        dir = os.path.dirname(__file__)
        self.file = os.path.join(dir, 'watcher', 'test.txt')

        factory = Mock()
        factory.factory = MagicMock(return_value='return')

        self.watcher = CoverageWatcher(self.file, factory)
        self.detected = threading.Event()
        self.delete()

    def tearDown(self):
        super(TestCoverageWatcher, self).tearDown()
        factory = self.watcher.get_coverage_factory()
        factory.factory.assert_called_once_with(self.file)

    def test_created(self):
        self.watcher.add_callback(CREATED, 1, lambda x: self.detect(x))
        self.watcher.start()
        self.create('created')
        self.assertTrue(self.detected.wait(1))

    def test_deleted(self):
        self.watcher.add_callback(DELETED, 1, lambda x: self.detect(x))
        self.create('deleted')
        self.watcher.start()
        self.delete()
        self.assertTrue(self.detected.wait(1))

    def test_modified(self):
        self.watcher.add_callback(MODIFIED, 1, lambda x: self.detect(x))
        self.create('modified1')
        self.watcher.start()
        self.modify('modified2')
        self.assertTrue(self.detected.wait(1))

    def test_unchanged(self):
        self.watcher.add_callback(UNCHANGED, 1, lambda x: self.detect(x))
        self.create('unchanged')
        self.watcher.start()
        self.modify('unchanged')
        self.assertTrue(self.detected.wait(1))

    def detect(self, data):
        "Perform callback parameter assertions and set detected event"
        self.assertEquals(data, 'return')
        self.detected.set()
