

def debug_message(message):
    """
    Prints a debug message to the Sublime console
    """
    from php_coverage.config import config
    if config.is_loaded() and config.debug:
        print("[PHPCoverage] " + str(message))
