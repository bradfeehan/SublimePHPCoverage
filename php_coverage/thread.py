import threading


class PollingThread(threading.Thread):

    """
    A Thread that polls a resource repeatedly, and which can be stopped
    by calling the stop() method.

    Override the poll() method in a subclass to define the behaviour of
    each "poll" event, which happens every self.tick() seconds.
    """

    def __init__(self):
        super(PollingThread, self).__init__()
        self.stop_event = threading.Event()

    def stop(self, timeout=None):
        """
        Stops the thread, blocking until it terminates. This can be
        called multiple times and will return immediately on subsequent
        invocations.
        """
        self.stop_event.set()
        self.join(timeout)
        if self.is_alive():
            raise Timeout("Timeout waiting for PollingThread to stop")

    def tick(self):
        """
        The timeout between polls, in seconds.
        """
        return 0.1  # seconds

    def run(self):
        """
        This method is called in the separate thread, and handles the
        scheduling of the polling. It waits for the stop event for
        up to self.tick() seconds, then stops if the stop event is set.
        If not, it calls self.poll() and resumes waiting again.
        """
        while True:
            # Effectively the same as time.sleep(self.tick()), but if
            # the stop event gets set, the thread wakes up immediately
            self.stop_event.wait(timeout=self.tick())

            # Terminate the method (and thread) if stop flag is set
            if (self.stop_event.is_set()):
                return

            # Delegate polling behaviour to subclass' poll() method
            self.poll()

    def poll(self):
        """
        Override in subclass to define polling behaviour
        """
        raise NotImplementedError("poll() should be overridden")


class NullPollingThread(PollingThread):

    """
    An example PollingThread which does nothing during its poll action.
    """

    def poll(self):
        """
        Do nothing.
        """
        pass


class Timeout(Exception):

    """
    An exception representing a timeout while trying to stop a thread.
    """

    def __str__():
        if len(args) > 0:
            return args[0]
        else:
            super(Timeout, self).__str__()
