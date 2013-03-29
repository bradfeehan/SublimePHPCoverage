import os
import sublime
import sublime_plugin
import subprocess
import xml.etree.ElementTree as ET


def find_project_root(file_path):
    """Project root is defined as the parent directory that contains a
    directory matching setting path_report'"""
    if os.access(os.path.join(file_path, Var.get('path_report')), os.R_OK):
        return file_path

    parent, current = os.path.split(file_path)
    if current:
        return find_project_root(parent)

class Var:
    @staticmethod
    def get(key):
        settings_project = sublime.active_window().active_view().settings()
        settings_file = sublime.load_settings('phpcoverage.sublime-settings')
        return settings_project.get('phpcoverage_' + key, settings_file.get(key))

    @staticmethod
    def path_project():
        return find_project_root(sublime.active_window().active_view().file_name())

def clear_markers(view):
    view.erase_status('SublimePHPCoverageBad')
    view.erase_status('SublimePHPCoverageGood')
    view.erase_regions('SublimePHPCoverageBad')
    view.erase_regions('SublimePHPCoverageGood')
    view.set_status('SublimePHPCoveragePercentage', '')

def debug_message(msg):
    if bool(Var.get('debug')) == True:
        print("[PHP Coverage] " + str(msg))

def shell_exec(cmd):
    debug_message('$ ' + cmd)

    info = None
    if os.name == 'nt':
        info = subprocess.STARTUPINFO()
        info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        info.wShowWindow = subprocess.SW_HIDE

    cwd = Var.path_project()
    debug_message("cwd: " + cwd)

    proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, startupinfo=info, cwd=cwd)
    if proc.stdout:
        debug_message(proc.communicate()[0].decode())
    return proc

class PhpcoverageClearMarkersCommand(sublime_plugin.ApplicationCommand):
    """Clear markers in any currently open files."""

    def run(self):
        for window in sublime.windows():
            for view in window.views():
                clear_markers(view)

class PhpcoverageUpdateCommand(sublime_plugin.TextCommand):
    """Highlight uncovered lines in the current file based on a previous
    coverage run."""

    def run(self, edit):
        view = self.view
        clear_markers(view)

        filename = view.file_name()
        debug_message('File: %s' % filename)

        # don't run for unsaved files
        if not filename:
            debug_message('Cannot run on unsaved file "' + filename + '".')
            return

        ext = os.path.splitext(filename)[1][1:].strip()
        ext_match = ext in Var.get('extensions')
        if ext_match != True:
            debug_message('Skipping file, filename does not match extensions array.')
            return

        project_root = find_project_root(filename)
        if not project_root:
            debug_message('Clover file not found (' + Var.get('path_report') + ').')
            return

        good = []
        bad = []

        coverage = os.path.join(project_root, Var.get('path_report'))
        root = ET.parse(coverage)

        for php_file in root.findall('./project//file'):
            if php_file.get('name') == filename:
                metrics = php_file.find('./metrics')
                loc = int(metrics.get('loc'))
                debug_message('Lines of code: %s' % loc)
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
                debug_message('Code coverage: %s' % coverage)
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

class PhpcoverageGenerateReport(sublime_plugin.ApplicationCommand):
    """Update code coverage report."""

    def run(self):
        debug_message('Generating code coverage report.')
        shell_exec(Var.get('coverage_update_command'))

class PhpcoverageEventListener(sublime_plugin.EventListener):
    """Event listener for the plugin"""
    def on_post_save(self, view):
        debug_message('Event: Post-Save')
        if bool(Var.get('coverage_update_on_save')) == True:
            sublime.run_command('phpcoverage_generate_report')
        if bool(Var.get('markers_update_on_save')) == True:
            sublime.run_command('phpcoverage_update_all')

    def on_load(self, view):
        if 'source.php' not in view.scope_name(0):
            return
        view.run_command('phpcoverage_update')
