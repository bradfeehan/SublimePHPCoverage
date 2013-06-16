import threading


def debug_message(message):
    """
    Prints a debug message to the Sublime console
    """
    from php_coverage.config import config
    if config.loaded and config.debug:
        thread = threading.current_thread().name
        print("[PHPCoverage] [%s] %s" % (str(thread), str(message)))
