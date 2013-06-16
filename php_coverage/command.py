import sublime_plugin

from php_coverage.data import CoverageDataFactory
from php_coverage.finder import CoverageFinder
from php_coverage.matcher import Matcher


class CoverageCommand(sublime_plugin.TextCommand):

    """
    Base class for a text command which has a coverage file.
    """

    def __init__(self, view, coverage_finder=None, matcher=None):
        super(CoverageCommand, self).__init__(view)
        self.coverage_finder = coverage_finder
        self.matcher = matcher

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
        Loads coverage data for the file open in the view which is
        running this command.
        """
        filename = self.view.file_name()
        coverage_file = self.get_coverage_finder().find(filename)
        if (coverage_file):
            return CoverageDataFactory().factory(coverage_file)

        return None

    def get_matcher(self):
        """
        Gets the matcher for the command. If none is set, it
        instantiates an instance of the default Matcher class.
        """
        if not self.matcher:
            self.matcher = Matcher()

        return self.matcher

    def should_include(self, filename):
        """
        Determines whether a file should be included or not.
        """
        return self.get_matcher().should_include(filename)
