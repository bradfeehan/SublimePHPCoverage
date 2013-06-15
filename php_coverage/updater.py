import os
import sublime
import xml.etree.ElementTree

from php_coverage.debug import debug_message


class ViewUpdater():

    """
    Handles updating the coverage data shown in a particular view.
    """

    def update(self, view, coverage):
        """
        Updates a view with the coverage data in a particular file
        """
        self.remove(view)

        self.annotate_lines(
            view=view,
            name='SublimePHPCoverageGood',
            lines=coverage.good_lines,
            scope='markup.inserted',
            icon='dot',
        )

        self.annotate_lines(
            view=view,
            name='SublimePHPCoverageBad',
            lines=coverage.bad_lines,
            scope='markup.deleted',
            icon='bookmark',
        )

        try:
            percentage = 100 * coverage.covered / float(coverage.statements)
        except ZeroDivisionError:
            percentage = 0

        status = '%d/%d lines (%.2f%%)' % (
            coverage.covered, coverage.statements, percentage)
        debug_message('Code coverage: %s' % status)
        view.set_status(
            'SublimePHPCoveragePercentage', 'Code coverage: %s' % status)

    def remove(self, view):
        view.erase_regions('SublimePHPCoverageBad')
        view.erase_regions('SublimePHPCoverageGood')
        view.erase_status('SublimePHPCoveragePercentage')

    def annotate_lines(self, view=None, name=None, lines=[], scope=None, icon=None, **kwargs):
        regions = []
        for line in lines:
            regions.append(view.full_line(view.text_point(line - 1, 0)))

        if len(regions) > 0:
            view.add_regions(name, regions, scope, icon, sublime.HIDDEN)
