import os
import sys
import sublime
import sublime_plugin

# Add current directory to Python's import path, to import php_coverage
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from php_coverage.command import CoverageCommand
from php_coverage.config import config
from php_coverage.debug import debug_message
from php_coverage.helper import set_timeout_async, sublime3
from php_coverage.mediator import ViewWatcherMediator
from php_coverage.updater import ViewUpdater
from php_coverage.watcher import FileWatcher


mediator = ViewWatcherMediator({
    FileWatcher.CREATED: lambda view, data: update_view(view, data),
    FileWatcher.MODIFIED: lambda view, data: update_view(view, data),
    FileWatcher.DELETED: lambda view, data: update_view(view, data),
})


def update_view(view, coverage=None):
    """
    Updates the coverage data displayed in a view.

    Arguments are the view to update, and the coverage data. The
    coverage data should be a CoverageData object, which contains
    the relevant coverage data for the file shown in the view. If the
    coverage data doesn't exist for the file shown in the view, or the
    coverage data is None, then the displayed coverage data will be
    removed from the view.
    """

    filename = view.file_name()
    debug_message('Updating coverage for ' + filename)

    file_coverage = coverage.get_file(filename) if coverage else None
    ViewUpdater().update(view, file_coverage)


def plugin_loaded():
    """
    Called automatically by Sublime when the API is ready to be used.
    Updates coverage for any open views, and adds them to the mediator.
    """

    config.load()

    # add open views to the mediator
    for window in sublime.windows():
        debug_message("[plugin_loaded] Found window %d" % window.id())
        for view in window.views():
            debug_message("[plugin_loaded] Found view %d" % view.id())
            mediator.add(view)
            set_timeout_async(
                lambda: view.run_command('phpcoverage_update'),
                1
            )

    debug_message("[plugin_loaded] Finished.")


class NewFileEventListener(sublime_plugin.EventListener):

    """
    An event listener that receives notifications about new files being
    opened in Sublime. Whenever a new file is opened or created, it
    creates a new FileWatcher for the relevant coverage file which
    contains the coverage data for the file being edited by the user.
    """

    def on_load_async(self, view):
        """
        Sets up a listener for the file that was just opened, and also
        update the code coverage to show it in the newly opened view.
        """
        mediator.add(view)
        view.run_command('phpcoverage_update')

    def on_load(self, view):
        """
        Synchronous fallback for on_load_async() for Sublime 2
        """
        if not sublime3:
            self.on_load_async(view)

    def on_close(self, view):
        """
        Unregister any listeners for the view that was just closed.
        """
        set_timeout_async(lambda: mediator.remove(view), 1)


class PhpcoverageUpdateCommand(CoverageCommand, sublime_plugin.TextCommand):

    """
    Updates the code coverage data for a file in a view.
    """

    def run(self, edit, coverage=None, **kwargs):
        filename = self.view.file_name()

        if filename is None:
            return

        if not self.should_include(filename):
            debug_message("Ignoring excluded file '%s'" % filename)
            return

        if not coverage:
            coverage = self.coverage()

        update_view(self.view, coverage)


class PhpcoverageUpdateAllCommand(CoverageCommand, sublime_plugin.TextCommand):

    """
    Updates the code coverage data for files in all open views.
    """

    def run(self, edit):
        windows = sublime.windows() or []

        for window in windows:
            views = window.views() or []

            for view in views:
                view.run_command("phpcoverage_update")


if not sublime3:
    plugin_loaded()
