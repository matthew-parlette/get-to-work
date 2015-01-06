class PluginMount(type):
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            # This branch only executes when processing the mount point itself.
            # So, since this is a new plugin type, not an implementation, this
            # class shouldn't be registered as a plugin. Instead, it sets up a
            # list where plugins can be registered later.
            cls.plugins = []
        else:
            # This must be a plugin implementation, which should be registered.
            # Simply appending it to the list is all that's needed to keep
            # track of it later.
            cls.plugins.append(cls)

class PluginProvider:
    """
    To define a plugin for the system, simply subclass this object.
    The __init__ should be called from your __init__ method, defined as:
        class Plugin(PluginProvider):
            def __init__(self, log, config):
                super(Trello, self).__init__(log, config)
                # Your plugin specific init code goes here
    Plugins should define one of the following, with the specified parameters:
        projects
    """
    __metaclass__ = PluginMount

    def __init__(self, log, config):
        log.info("Registering %s as a PluginProvider" % str(self.__class__.__name__))
        self.log = log
        self.config = config
        self.name = "plugin" # Friendly name to reference this plugin
        self.icon = "plug" # Icon to use for items from this plugin.

    def projects(self, filter = {}):
        """Return a list of projects from this plugin."""
        return []

    def tasks(self, project = None):
        """Return a list of tasks.

        If project is provided, return tasks for a single Project"""
        return []

    def comments(self, task = None):
        """Return a list of Comment objects.

        If task is provided, return comments for a single Task."""
        return []

    def complete(self, task = None):
        """Mark a given Task as complete."""
        return False

    def add_comment(self, task, text):
        """Add a Comment to a given Task."""
        return False

    def report(self,date):
        """Return a string for the report with the filters provided."""
        return None
