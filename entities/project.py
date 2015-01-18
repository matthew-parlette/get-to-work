class Project(object):
    def __init__(
        self,
        name = None,
        pid = None,
        plugin = None,
        plugin_obj = None,
        url = None,
        tasks = None
    ):
        super(Project, self).__init__()
        self.name = name             # Project name
        self.pid = pid               # Identifier for this project (relating to source)
        self.plugin = plugin         # Where is this project stored (ex: Trello)
        self.plugin_obj = plugin_obj # Reference to the object that created this project
        self.url = url               # Link to the project
        self.tasks = tasks           # List of tasks for this project

    def __repr__(self):
        return "%s (%s tasks)" % (
            self.name,
            str(len(self.tasks)),
        )
