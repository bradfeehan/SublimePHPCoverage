import os
import sys
import sublime
import sublime_plugin

# Add current directory to Python's import path, to import php_coverage
sys.path.append(os.path.dirname(__file__))
from php_coverage.command import CoverageCommand
from php_coverage.debug import debug_message
from php_coverage.mediator import ViewWatcherMediator
from php_coverage.updater import ViewUpdater
from php_coverage.watcher import FileWatcher


mediator = ViewWatcherMediator({
    FileWatcher.CREATED: lambda view, data: update_view(view, data),
    FileWatcher.MODIFIED: lambda view, data: update_view(view, data),
    FileWatcher.DELETED: lambda view, data: update_view(view, data),
})


def update_view(view, coverage):
    """
    Updates the coverage data displayed in a view.

    Arguments are the view to update, and the coverage data. The
    coverage data should be a CoverageData object, which contains
    the relevant coverage data for the file shown in the view. If the
    coverage data doesn't exist for the file shown in the view, or the
    coverage data is None, then the displayed coverage data will be
    removed from the view.
    """
    if not coverage:
        return

    filename = view.file_name()
    debug_message('Updating coverage for ' + filename)

    file_coverage = coverage.get_file(filename)
    if file_coverage:
        ViewUpdater().update(view, file_coverage)
    else:
        debug_message("No coverage data found for %s" % filename)


def plugin_loaded():
    """
    Called automatically by Sublime when the API is ready to be used.
    Updates coverage for any open views, and adds them to the mediator.
    """

    # add open views to the mediator
    for window in sublime.windows():
        debug_message("[plugin_loaded] Found window %d" % window.id())
        for view in window.views():
            debug_message("[plugin_loaded] Found view %d" % view.id())
            mediator.add(view)
            sublime.set_timeout_async(
                lambda: view.run_command('php_coverage_update')
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
        view.run_command('php_coverage_update')

    def on_close(self, view):
        """
        Unregister any listeners for the view that was just closed.
        """
        sublime.set_timeout_async(lambda: mediator.remove(view))


class PhpCoverageUpdateCommand(CoverageCommand, sublime_plugin.TextCommand):

    """
    Updates the code coverage data for a file in a view.
    """

    def run(self, edit, coverage=None, **kwargs):
        filename = self.view.file_name()
        if not coverage:
            coverage = self.coverage()

        update_view(self.view, coverage)
