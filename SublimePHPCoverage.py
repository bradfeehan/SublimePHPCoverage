import os
import sys

# Add current directory to Python's import path, to import php_coverage
sys.path.append(os.path.dirname(__file__))
import php_coverage.debug

debug_message = php_coverage.debug.debug_message


def plugin_loaded():
    debug_message("entering plugin_loaded()")
