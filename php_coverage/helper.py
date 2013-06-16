import sublime
from php_coverage.debug import debug_message


sublime3 = int(sublime.version()) >= 3000

if sublime3:
    set_timeout_async = sublime.set_timeout_async
else:
    debug_message("Adding Sublime 3 polyfills")
    set_timeout_async = sublime.set_timeout
