class Comment(object):
    def __init__(
        self,
        name = None,
        plugin = None,
        url = None,
        timestamp = None,
    ):
        super(Comment, self).__init__()
        self.name = name.encode(
            'utf-8',
            'ignore'
        )                           # Comment text (encoding should avoid unicode issues)
        self.plugin = plugin        # Where is this comment from? (ex: Trello)
        self.url = url              # Link to the item (if present)
        self.timestamp = timestamp  # Timestamp when the comment was made

    def __repr__(self):
        return "%s (%s)" % (self.name[10:],str(self.timestamp))