class Task(object):
    def __init__(
        self,
        name = None,
        source = None,
        url = None,
        status = None
    ):
        super(Task, self).__init__()
        self.name = name     # Project name
        self.source = source # Where is this task from? (ex: Trello)
        self.url = url       # Link to the item
        self.status = status # Status of this task
