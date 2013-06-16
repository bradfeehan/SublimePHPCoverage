import os

from php_coverage.debug import debug_message
from php_coverage.finder import CoverageFinder
from php_coverage.helper import set_timeout_async
from php_coverage.matcher import Matcher
from php_coverage.watcher import CoverageWatcher


class ViewWatcherMediator():

    """
    Mediates between views and CoverageWatchers.

    The "callbacks" parameter is a dictionary mapping CoverageWatcher
    events to a callback which should be run when that event occurs to
    the coverage file for a view which has been added. The callback
    will be passed the view whose coverage data file has experienced
    the event, as well as a CoverageData object representing the new
    content of the file.

    When calling add(view), a CoverageWatcher will be set up to watch
    the file containing that view's coverage data. When the watcher
    detects an event, this mediator will pass the relevant view to the
    callback so that it can be informed about changes to its code
    coverage data.

    This class re-uses CoverageWatchers, so if there's multiple views
    that need to be notified about the same coverage file, there will
    be only one CoverageWatcher created.

    Calling remove(view) will de-register any watchers that were set
    up for a view by add(view). If this results in a CoverageWatchers
    having no more registered callbacks, that CoverageWatchers will be
    stopped. A new CoverageWatchers will be created and started next
    time a view is added using add(view).
    """

    def __init__(self, callbacks={}, coverage_finder=None, matcher=None):
        self.coverage_finder = coverage_finder or CoverageFinder()
        self.matcher = matcher or Matcher()
        self.callbacks = callbacks
        self.watchers = {}

    def add(self, view):
        """
        Sets up a watcher for a newly opened view.
        """
        # find coverage file for the view's file
        filename = view.file_name()

        if not self.matcher.should_include(filename):
            debug_message("Ignoring excluded file '%s'" % filename)
            return

        coverage = self.coverage_finder.find(filename)

        # nothing can be done if the coverage file can't be found
        if not coverage:
            return

        # ensure a CoverageWatcher exists for the coverage file
        if not coverage in self.watchers:
            debug_message("Creating CoverageWatcher for " + coverage)
            self.watchers[coverage] = CoverageWatcher(coverage)
        else:
            debug_message("Found existing CoverageWatcher for " + coverage)

        watcher = self.watchers[coverage]

        # add callbacks as defined at construction time, also adding in
        # the relevant view as a parameter to the callback
        for event, callback in self.callbacks.items():
            wrapped = self.prepare_callback(callback, view)
            watcher.add_callback(event, view.id(), wrapped)

        # start the watcher if it's not already running
        if not watcher.is_alive():
            debug_message("Starting CoverageWatcher for " + coverage)
            watcher.start()

    def prepare_callback(self, callback, view):
        """
        Wraps a callback function in a lambda to add a view as an
        additional parameter, and to be run in the main thread.
        """
        return lambda data: set_timeout_async(lambda: callback(view, data), 1)

    def remove(self, view):
        """
        Unregisters any set-up listeners for a recently closed view.
        """
        # loop over the watchers
        for id, watcher in list(self.watchers.items()):
            # delete any callback related to this view
            watcher.remove_callback(view.id())

            # if no more callbacks on this watcher, stop and remove it
            if not watcher.has_callbacks():
                filename = watcher.filename
                debug_message("Stopping CoverageWatcher for '%s'" % filename)
                watcher.stop(1)
                del self.watchers[id]
