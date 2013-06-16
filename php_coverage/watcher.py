import hashlib
import os

from php_coverage.data import CoverageDataFactory
from php_coverage.debug import debug_message
from php_coverage.thread import PollingThread

# Chunk size used to read file in
CHUNK_SIZE = 1024 * 1024


class FileWatcher(PollingThread):

    """
    Watches a file for changes, calling a callback every time the file
    is modified.
    """

    CREATED = 'created'      # didn't exist before, does now
    DELETED = 'deleted'      # existed before, doesn't now
    MODIFIED = 'modified'    # mtime changed, different content
    UNCHANGED = 'unchanged'  # mtime changed, same content

    def __init__(self, filename):
        super(FileWatcher, self).__init__()
        self.filename = filename
        self.callbacks = {
            self.CREATED: {},
            self.DELETED: {},
            self.MODIFIED: {},
            self.UNCHANGED: {},
        }

    def add_callback(self, events, id, callback):
        """
        Adds a new callback function for particular events. When one of
        the events in "events" occurs, callback will be called without
        any arguments.
        """
        # make events a list if only one passed in
        if type(events) is not list:
            events = [events]

        # add callback to each event in events
        for event in events:
            if not id in self.callbacks[event]:
                self.callbacks[event][id] = callback

    def has_callbacks(self):
        """
        Determines whether or not this FileWatcher has any callbacks.
        Returns True if at least one callback exists for at least one
        event, otherwise False.
        """
        for callbacks in self.callbacks.values():
            for callback in callbacks.values():
                return True

        return False

    def remove_callback(self, id):
        """
        Removes an existing callback for particular events. The "id"
        parameter identifies the callback by the same "id" parameter
        passed to add_callback() initally.
        """
        # remove callback from each event, if it exists
        for event in self.callbacks:
            if id in self.callbacks[event]:
                del self.callbacks[event][id]

    def dispatch(self, event):
        """
        Dispatches an event, calling all relevant callbacks.
        """
        callbacks = self.callbacks[event]

        debug_message("[FileWatcher] %s '%s'" % (event, self.filename))
        debug_message("[FileWatcher] %d callbacks" % len(callbacks))

        for callback in callbacks.values():
            debug_message("[FileWatcher] Calling %s" % repr(callback))
            callback()

    def hash(self):
        """
        Gets the hash of the file referred to by self.filename. Returns
        None if the file doesn't exist.
        """
        if not os.path.exists(self.filename):
            return None

        sha1 = hashlib.sha1()
        with open(self.filename, 'rb') as f:
            while True:
                data = f.read(CHUNK_SIZE)
                if not data:
                    break
                sha1.update(data)

        return sha1.digest()

    def mtime(self):
        """
        Gets the last modified time of the file referred to by
        self.filename. Returns None if the file doesn't exist.
        """
        if not os.path.exists(self.filename):
            return None

        return os.path.getmtime(self.filename)

    def start(self):
        self.last_mtime = self.mtime()
        self.last_hash = self.hash()
        if self.last_mtime:
            debug_message("[FileWatcher] exists: %s" % self.filename)
        else:
            debug_message("[FileWatcher] doesn't exist: %s" % self.filename)
        super(FileWatcher, self).start()

    def poll(self):
        """
        Checks the modified time of the file and dispatches events
        representing any changes to it.
        """
        new_mtime = self.mtime()

        # if unchanged, do nothing
        if self.last_mtime == new_mtime:
            return

        new_hash = self.hash()

        # otherwise dispatch the corresponding event
        if not self.last_mtime:
            self.dispatch(self.CREATED)
        elif not new_mtime:
            self.dispatch(self.DELETED)
        elif self.last_hash != new_hash:
            self.dispatch(self.MODIFIED)
        else:
            self.dispatch(self.UNCHANGED)

        # save new mtime for next poll
        self.last_mtime = new_mtime
        self.last_hash = new_hash


class CoverageWatcher(FileWatcher):

    """
    A FileWatcher which looks for changes to a coverage file, and
    passes extra coverage-related data to the event callbacks.
    """

    def __init__(self, filename, coverage_factory=None):
        super(CoverageWatcher, self).__init__(filename)
        self.coverage_factory = coverage_factory

    def get_coverage_factory(self):
        """
        Gets the coverage factory for this CoverageWatcher. If none is
        set, it instantiates an instance of the CoverageDataFactory
        class as a default.
        """
        if not self.coverage_factory:
            self.coverage_factory = CoverageDataFactory()

        return self.coverage_factory

    def dispatch(self, event):
        """
        Dispatches an event, calling all relevant callbacks.

        Overridden to pass coverage data to the callback, taken from
        the coverage file being watched by this CoverageWatcher.
        """
        callbacks = self.callbacks[event]

        debug_message("[CoverageWatcher] %s '%s'" % (event, self.filename))
        debug_message("[CoverageWatcher] %d callbacks" % len(callbacks))

        data = self.get_coverage_factory().factory(self.filename)

        for callback in callbacks.values():
            debug_message("[CoverageWatcher] Calling %s" % repr(callback))
            callback(data)
