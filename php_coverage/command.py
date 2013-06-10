import sublime_plugin
from php_coverage.finder import CoverageFinder


class CoverageCommand(sublime_plugin.TextCommand):

    """
    Base class for a text command which has a coverage file.
    """

    def __init__(self, view, coverage_finder=None):
        super(CoverageCommand, self).__init__(view)
        self.coverage_finder = coverage_finder

    def get_coverage_finder(self):
        """
        Gets the coverage finder for the command. If none is set, it
        instantiates an instance of the default CoverageFinder class.
        """
        if not self.coverage_finder:
            self.coverage_finder = CoverageFinder()

        return self.coverage_finder

    def coverage(self):
        """
        Finds the coverage file which contains coverage data for the
        file open in the view which is running this command.
        """
        return self.get_coverage_finder().find(self.view.file_name())
