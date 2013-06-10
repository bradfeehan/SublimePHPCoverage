import os

from php_coverage.debug import debug_message
from php_coverage.finder import CoverageFinder
from php_coverage.watcher import FileWatcher


class ViewWatcherMediator():

    """
    Mediates between views and FileWatchers.

    The "callbacks" parameter is a dictionary mapping FileWatcher
    events to a callback which should be run when that event occurs to
    the coverage file for a view which has been added. The callback
    will be passed the view whose coverage data file has experienced
    the event.

    When calling add(view), a FileWatcher will be set up to watch the
    file containing that view's coverage data. When the watcher detects
    an event, this mediator will pass the relevant view to the callback
    so that it can be informed about changes to its code coverage data.

    This class re-uses FileWatchers, so if there's multiple views that
    need to be notified about the same coverage file, there will be
    only one FileWatcher created.

    Calling remove(view) will de-register any watchers that were set
    up for a view by add(view). If this results in a FileWatchers
    having no more registered callbacks, that FileWatcher will be
    stopped. A new FileWatcher will be created and started next time a
    view is added using add(view).
    """

    def __init__(self, callbacks={}, coverage_finder=None):
        self.coverage_finder = coverage_finder or CoverageFinder()
        self.callbacks = callbacks
        self.watchers = {}

    def add(self, view):
        """
        Sets up a watcher for a newly opened view.
        """
        # find coverage file for the view's file
        filename = view.file_name()
        coverage = self.coverage_finder.find(filename)

        # nothing can be done if the coverage file can't be found
        if not coverage:
            return

        # ensure a FileWatcher exists for the coverage file
        if not coverage in self.watchers:
            debug_message("Creating FileWatcher for " + coverage)
            self.watchers[coverage] = FileWatcher(coverage)
        else:
            debug_message("Found existing FileWatcher for " + coverage)

        watcher = self.watchers[coverage]

        # add callbacks as defined at construction time, also adding in
        # the relevant view as a parameter to the callback
        for event, callback in self.callbacks.items():
            watcher.add_callback(event, view.id(), lambda: callback(view))

        # start the watcher if it's not already running
        if not watcher.is_alive():
            debug_message("Starting FileWatcher for " + coverage)
            watcher.start()

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
                debug_message("Stopping FileWatcher for " + watcher.filename)
                watcher.stop(1)
                del self.watchers[id]
