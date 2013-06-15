import os
import sys
import sublime
import sublime_plugin

# Add current directory to Python's import path, to import php_coverage
sys.path.append(os.path.dirname(__file__))
from php_coverage.command import CoverageCommand
from php_coverage.debug import debug_message
import php_coverage.finder
import php_coverage.mediator
import php_coverage.updater
import php_coverage.watcher

CREATED = php_coverage.watcher.FileWatcher.CREATED
DELETED = php_coverage.watcher.FileWatcher.DELETED
MODIFIED = php_coverage.watcher.FileWatcher.MODIFIED


mediator = php_coverage.mediator.ViewWatcherMediator({
    CREATED: lambda v: v.run_command("php_coverage_update"),
    MODIFIED: lambda v: v.run_command("php_coverage_update"),
    DELETED: lambda v: v.run_command("php_coverage_remove"),
})


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

    def run(self, edit):
        debug_message('Updating coverage for ' + self.view.file_name())
        updater = php_coverage.updater.ViewUpdater()
        finder = php_coverage.finder.CoverageFinder()
        coverage = finder.find(self.view.file_name())

        if coverage:
            updater.update(self.view, coverage)
