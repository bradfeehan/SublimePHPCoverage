import re

from php_coverage.config import config


class Matcher():

    """
    Matches filenames against patterns to determine whether to include
    them or not.
    """

    def should_include(self, filename):
        """
        Determines whether to include a file or not based on its
        filename and the settings in the plugin configuration.
        """
        return self.included(filename) and not self.excluded(filename)

    def included(self, filename):
        """
        Determines whether a filename is on the "include" list.
        """
        return self.match(config.include, filename)

    def excluded(self, filename):
        """
        Determines whether a filename is on the "exclude" list.
        """
        return self.match(config.exclude, filename)

    def match(self, patterns, string):
        """
        Determines whether a string matches any of a list of patterns.
        """
        for pattern in patterns:
            if re.search(pattern, string):
                return True

        # no patterns matched
        return False
