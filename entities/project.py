class Project(object):
    def __init__(
        self,
        name = None,
        source = None,
        url = None,
        tasks = None
    ):
        super(Project, self).__init__()
        self.name = name     # Project name
        self.source = source # Where is this project stored (ex: Trello)
        self.url = url       # Link to the project
        self.tasks = tasks   # List of tasks for this project
