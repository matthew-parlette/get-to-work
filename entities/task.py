class Task(object):
    def __init__(
        self,
        name = None,
        source = None,
        url = None,
        status = None,
        priority = None,
    ):
        super(Task, self).__init__()
        self.name = name         # Task name
        self.source = source     # Where is this task from? (ex: Trello)
        self.url = url           # Link to the item
        self.status = status     # Status of this task
        self.priority = priority # Priority of this task (low, medium, high)

    def __repr__(self):
        return "%s (%s, %s)" % (
            self.name,
            str(self.status),
            str(self.priority),
        )
