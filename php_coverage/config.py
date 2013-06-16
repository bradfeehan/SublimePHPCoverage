from php_coverage.debug import debug_message


class Config():

    """
    Handles retrieval of plugin settings.
    """

    keys = [
        "debug",
        "report_path",
        "include",
        "exclude",
    ]

    def __init__(self):
        self.loaded = False

    def load(self):
        """
        Loads the settings from disk into structured data.
        """
        debug_message('[config] Loading config')
        import sublime

        self.filename = "SublimePHPCoverage.sublime-settings"
        self.settings = sublime.load_settings(self.filename)
        self.project = {}

        if sublime.active_window() is not None:
            debug_message('[config] Window is active, loading project')
            project = sublime.active_window().active_view().settings()

            if project.has('phpcoverage'):
                debug_message("[config] Found project settings")
                project.clear_on_change('phpcoverage')
                self.project = project.get('phpcoverage')
                project.add_on_change('phpcoverage', config.load)
            else:
                debug_message("[config] No 'phpcoverage' key, ignoring")

        for key in self.keys:
            self.settings.clear_on_change(key)
            setattr(self, key, self.get_setting(key))
            self.settings.add_on_change(key, config.load)

        self.loaded = True

    def is_loaded(self):
        """
        Determines whether or not the settings have been loaded.
        """
        return self.loaded

    def get_setting(self, key):
        """
        Gets a configuration value by key.
        """
        if key in self.project:
            value = self.project.get(key)
            debug_message("[config] [project] %s: '%s'" % (key, value))
            return value
        else:
            value = self.settings.get(key, None)
            debug_message("[config]: %s: '%s'" % (key, value))
            return value

    def __getattr__(self, key):
        """
        Raise exception when retrieving configuration settings before
        load() is called.
        """
        if key in self.keys:
            if not self.is_loaded():
                raise ConfigurationNotLoaded()
            else:
                raise AttributeError("Unknown configuration key '%s'" % key)


class ConfigurationNotLoaded(Exception):

    """
    An exception representing an attempt to retrieve a configuration
    key before the configuration has been loaded.
    """

    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        if not self.message:
            self.message = "Configuration not ready yet"

        return self.message

config = Config()
