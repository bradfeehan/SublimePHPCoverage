import os
import sublime
import xml.etree.ElementTree
from php_coverage.debug import debug_message


class ViewUpdater():

    """
    Handles updating the coverage data shown in a particular view.
    """

    def update(self, view, coverage_file):
        """
        Updates a view with the coverage data in a particular file
        """
        self.remove(view)

        filename = view.file_name()
        data = self.get_coverage_data(coverage_file, filename)

        if not data:
            debug_message("No %s coverage in %s" % (filename, coverage_file))
            return

        regions = {
            "good": [],
            "bad": [],
        }

        for line in data["good"]:
            regions["good"].append(
                view.full_line(view.text_point(line - 1, 0)))

        for line in data["bad"]:
            regions["bad"].append(view.full_line(view.text_point(line - 1, 0)))

        if regions["bad"]:
            view.add_regions(
                'SublimePHPCoverageGood',
                regions["bad"],
                'markup.deleted',
                'bookmark',
                sublime.HIDDEN
            )

        if regions["good"]:
            view.add_regions(
                'SublimePHPCoverageBad',
                regions["good"],
                'markup.inserted',
                'dot',
                sublime.HIDDEN
            )

        try:
            percentage = 100 * data["covered"] / float(data["total"])
        except ZeroDivisionError:
            percentage = 0

        status = '%d/%d lines (%.2f%%)' % (
            data["covered"], data["total"], percentage)
        debug_message('Code coverage: %s' % status)
        view.set_status(
            'SublimePHPCoveragePercentage', 'Code coverage: %s' % status)

    def remove(self, view):
        view.erase_regions('SublimePHPCoverageBad')
        view.erase_regions('SublimePHPCoverageGood')
        view.erase_status('SublimePHPCoveragePercentage')

    def get_coverage_data(self, coverage_file, filename):
        """
        Extracts the coverage data from a coverage file for a
        particular filename.
        """

        good = []
        bad = []

        # root XML element of the coverage file
        root = xml.etree.ElementTree.parse(coverage_file)

        for php_file in root.findall('./project//file'):
            if self.same_path(php_file.get('name'), filename):
                # found the correct file
                metrics = php_file.find('./metrics')
                loc = int(metrics.get('loc'))
                debug_message('Found %s lines in %s' % (loc, filename))

                for line in php_file.findall('line'):
                    # skip non-statement lines
                    if line.get('type') != 'stmt':
                        continue

                    num = int(line.get('num'))
                    count = int(line.get('count'))

                    # quirks in the coverage data: skip line #0 and any
                    # lines greater than the number of lines in the file
                    if num > loc or num == 0:
                        continue

                    if count > 0:
                        good.append(num)
                    else:
                        bad.append(num)

                covered = int(metrics.get('coveredstatements'))
                total = int(metrics.get('statements'))
                percentage = 100 * covered / float(total)

                return {
                    "good": good,
                    "bad": bad,
                    "covered": covered,
                    "total": total
                }

        return None

    def same_path(self, path1, path2):
        """
        Determines if two file paths are the same. Performs
        normalisation before comparison to avoid cross-platform issues
        with path separators.
        """
        return os.path.realpath(path1) == os.path.realpath(path2)
