import sublime, sublime_plugin


def plugin_loaded():
    debug_message("entering plugin_loaded()")


def debug_message(message):
    print("[PHPCoverage] " + str(message))
