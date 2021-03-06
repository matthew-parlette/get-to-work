class Task(object):
    def __init__(
        self,
        name = None,
        id = None,
        plugin = None,
        plugin_obj = None,
        url = None,
        requestor = None,
        status = None,
        priority = None,
        comments = [],
        commentable = True,
        closeable = True,
    ):
        super(Task, self).__init__()
        self.name = name               # Task name
        self.id = id                   # ID associated with task from plugin
        self.plugin = plugin           # The plugin that created this task
        self.plugin_obj = plugin_obj   # Reference to the object that created this task
        self.url = url                 # Link to the item
        self.requestor = requestor     # Who is this task for? Generally this is a customer
        self.status = status           # Status of this task
        self.priority = priority       # Priority of this task (low, medium, high)
        self._comments = comments      # Comments for this task
        self.commentable = commentable # Can a comment be added through this site?
        self.closeable = closeable     # Can this task be closed through this site?

    def __repr__(self):
        return "%s (%s, %s)" % (
            self.name,
            str(self.status),
            str(self.priority),
        )

    @property
    def comments(self):
        if not self._comments:
            if self.plugin and self.plugin_obj:
                self._comments = self.plugin.comments(self)
        return self._comments
