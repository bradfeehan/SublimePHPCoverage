import os
import xml.etree.ElementTree


class CoverageData():

    """
    Represents a coverage data file.
    """

    def __init__(self, coverage_file):
        self.coverage_file = coverage_file
        self.elements = None
        self.files = {}

    def is_loaded(self):
        """
        Checks if the XML data is loaded from the coverage file.
        """
        return not self.elements is None

    def load(self):
        """
        Loads the XML data from the coverage file.
        """
        self.files = {}
        if os.path.exists(self.coverage_file):
            root = xml.etree.ElementTree.parse(self.coverage_file)
            self.elements = root.findall('./project//file')
        else:
            self.elements = []

    def normalise(self, filename):
        """
        Normalises a filename to aid comparisons.
        """
        return os.path.normcase(os.path.realpath(filename))

    def get_file(self, filename):
        """
        Gets a FileCoverage object for a particular source file, which
        will represent the coverage data for that source file.
        """
        if not self.is_loaded():
            self.load()

        filename = self.normalise(filename)

        # check in self.files cache
        if filename not in self.files:
            self.files[filename] = None

            # find coverage data in the parsed XML coverage file
            for data in self.elements:
                if self.normalise(data.get('name')) == filename:
                    # create FileCoverage with the data
                    self.files[filename] = FileCoverage(filename, data)

        return self.files[filename]


class CoverageDataFactory():

    """
    Creates instances of CoverageData objects.
    """

    def __init__(self, class_name=CoverageData):
        self.class_name = class_name

    def factory(self, coverage_file):
        return self.class_name(coverage_file)


class FileCoverage():

    """
    Represents coverage data for a single file.
    """

    def __init__(self, filename, data):
        self.filename = filename
        self.data = data
        self.parsed = False

    def is_parsed(self):
        """
        Determines whether the coverage data has been parsed into
        structured data.
        """
        return self.parsed

    def parse(self):
        """
        Parses the coverage data into structured data.
        """
        metrics = self.data.find('./metrics')

        self.num_lines = int(metrics.get('loc'))
        self.covered = int(metrics.get('coveredstatements'))
        self.statements = int(metrics.get('statements'))

        self.good_lines = []
        self.bad_lines = []

        for line in self.data.findall('line'):
            # skip non-statement lines
            if line.get('type') != 'stmt':
                continue

            line_number = int(line.get('num'))
            test_count = int(line.get('count'))

            # quirks in the coverage data: skip line #0 and any
            # lines greater than the number of lines in the file
            if line_number == 0 or line_number > self.num_lines:
                continue

            # add this line number to good_lines or bad_lines depending
            # on whether it's covered by at least one test or not
            dest = self.good_lines if test_count > 0 else self.bad_lines
            dest.append(line_number)

        self.parsed = True

    def __getattr__(self, name):
        """
        Automatically parse when attempting to retrieve output values.
        """
        methods = [
            'num_lines',
            'covered',
            'statements',
            'good_lines',
            'bad_lines',
        ]

        if name in methods:
            if not self.is_parsed():
                self.parse()

            return getattr(self, name)

        raise AttributeError()
