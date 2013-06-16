import os

from php_coverage.config import config
from php_coverage.debug import debug_message


class CoverageFinder():

    """
    Finds the filename containing coverage data for a particular file.
    Currently it ascends through parent directories, until it finds
    "build/logs/clover.xml".
    """

    def find(self, filename):
        """
        Finds the coverage file for a given filename.
        """
        # start from the file's directory
        parent, current = os.path.split(os.path.abspath(filename))
        path = os.path.normcase(os.path.normpath(config.report_path))

        # iterate through parent directories until coverage file found
        while current:
            coverage = os.path.join(parent, path)
            if os.path.exists(coverage):
                debug_message("Coverage for %s in %s" % (filename, coverage))
                return coverage

            parent, current = os.path.split(parent)

        debug_message("Coverage file not found for " + str(filename))
        return None
