import os

from php_coverage.debug import debug_message


class CoverageFinder():

    """
    Finds the filename containing coverage data for a particular file.
    Currently it ascends through parent directories, until it finds
    "build/logs/clover.xml".

    TODO: Find the coverage file based on a configurable plugin setting
    """

    def find(self, filename):
        """
        Finds the coverage file for a given filename.
        """
        # start from the file's directory
        dir = os.path.abspath(os.path.dirname(filename))

        # iterate through parent directories until coverage file found
        while len(dir) > 3:
            coverage = os.path.join(dir, 'build', 'logs', 'clover.xml')
            if os.path.exists(coverage):
                debug_message("Coverage for %s in %s" % (filename, coverage))
                return coverage
            dir = os.path.dirname(dir)

        debug_message("Coverage file not found for " + str(filename))
        return None
