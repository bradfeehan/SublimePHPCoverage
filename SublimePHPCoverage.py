import os
import sublime
import sublime_plugin
import xml.etree.ElementTree as ET


def find_project_root(file_path):
    """Project root is defined as the parent directory that contains a
    directory called 'tests/coverage'"""
    if os.access(os.path.join(file_path, 'tests/coverage'), os.R_OK):
        return file_path

    parent, current = os.path.split(file_path)
    if current:
        return find_project_root(parent)


class SublimePHPCoverageListener(sublime_plugin.EventListener):
    """Event listener to highlight uncovered lines when a PHP file is
    loaded"""

    def on_load(self, view):
        if 'source.php' not in view.scope_name(0):
            return

        view.run_command('phpcoverage_update')


class PhpcoverageUpdateCommand(sublime_plugin.TextCommand):
    """Highlight uncovered lines in the current file based on a previous
    coverage run."""

    def run(self, edit):
        view = self.view

        # clean up
        view.erase_status('SublimePHPCoverageBad')
        view.erase_status('SublimePHPCoverageGood')
        view.erase_regions('SublimePHPCoverageBad')
        view.erase_regions('SublimePHPCoverageGood')
        view.set_status('SublimePHPCoveragePercentage', '')

        filename = view.file_name()
        print 'SublimePHPCoverage: Filename: %s' % filename

        # don't run for unsaved files
        if not filename:
            print 'SublimePHPCoverage: Not running for unsaved file'
            return

        project_root = find_project_root(filename)
        if not project_root:
            print 'SublimePHPCoverage: Could not find coverage directory.'
            return

        good = []
        bad = []

        coverage = os.path.join(project_root, 'tests/coverage/clover.xml')
        root = ET.parse(coverage)

        for php_file in root.findall('./project//file'):
            if php_file.get('name') == filename:
                metrics = php_file.find('./metrics')
                loc = int(metrics.get('loc'))
                print 'SublimePHPCoverage: lines of code: %s' % loc
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

                    # subtract 1 for zero-based index used by Sublime
                    region = view.full_line(view.text_point(num - 1, 0))

                    if count > 0:
                        good.append(region)
                    else:
                        bad.append(region)
                covered = int(metrics.get('coveredstatements'))
                total = int(metrics.get('statements'))
                percentage = 100 * covered / float(total)
                coverage = '%d/%d lines (%.2f%%)' % (covered, total, percentage)
                print 'Code coverage: %s' % coverage
                view.set_status('SublimePHPCoveragePercentage', 'Code coverage: %s' % coverage)
                break

        # update highlighted regions
        if bad:
            view.add_regions('SublimePHPCoverageGood', bad, 'markup.deleted', 'bookmark', sublime.HIDDEN)
        if good:
            view.add_regions('SublimePHPCoverageBad', good, 'markup.inserted', 'dot', sublime.HIDDEN)


class PhpcoverageUpdateAllCommand(sublime_plugin.ApplicationCommand):
    """Update code coverage highlights in any currently open files."""

    def run(self):
        for window in sublime.windows():
            for view in window.views():
                view.run_command('phpcoverage_update')
