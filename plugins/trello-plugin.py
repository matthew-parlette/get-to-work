from plugin import PluginProvider
from trello import TrelloClient, util
from entities import *
from datetime import datetime
import timeit

# Reference for py-trello 1.6:
# https://github.com/sarumont/py-trello/blob/c12b65d238970dad0258c54e5d840bfb1d293cee/trello/__init__.py

class Trello(PluginProvider):
    """docstring for Trello"""
    def __init__(self, log, config):
        super(Trello, self).__init__(log, config)
        self.name = 'trello' # Friendly name for this plugin source
        self.icon = 'trello'
        self.log.info("Initializing Trello client...")

        # Gather the oauth tokens if they weren't provided
        # if config['trello']['oauth_token'] == "":
        #     # Need to get the trello oauth_token and oauth_token_secret
        #     log.debug("Retrieving Trello oauth token...")
        #     os.environ["TRELLO_API_KEY"] = config["trello"]["key"]
        #     os.environ["TRELLO_API_SECRET"] = config["trello"]["secret"]
        #     os.environ["TRELLO_EXPIRATION"] = 'never'
        #     trello.util.create_oauth_token()

        # Establish the Trello client connection
        self.api = TrelloClient(
            self.config['trello']['key'],
            self.config['trello']['secret'],
            self.config['trello']['oauth_token'],
            self.config['trello']['oauth_token_secret']
        )
        self.log.info("Trello client initialized")

    def projects(self, filter = {}):
        result = []
        for board in self.api.list_boards():
            self.log.debug("Processing board %s..." % str(board))
            if board.closed:
                self.log.debug("Board %s is closed, skipping..." % str(board))
                continue
            # Build task list
            lists = board.open_lists()
            tasks = []
            for card in board.open_cards():
                self.log.debug("Card %s has badges %s" % (str(card.name),str(card.badges)))
                for board_list in lists:
                    if board_list.id == card.list_id:
                        if board_list.name in self.config['trello']['status']:
                            status = self.config['trello']['status'][board_list.name]
                            self.log.debug("Status for '%s' read as %s" % (str(card.name),str(status)))
                        else:
                            self.log.error(
                                "Status for '%s' could not be determined, list name of %s not found in config" % (
                                    str(card.name),
                                    str(board_list.name),
                                ))
                        break

                # Determine priority
                priority = None
                if card.labels:
                    for label in card.labels:
                        if label['name'] in self.config['trello']['priority']:
                            # Return the first label we find that matches a priority
                            #  from the config.
                            priority = self.config['trello']['priority'][label['name']]
                            break

                tasks += [task.Task(
                    name = card.name,
                    id = card.id,
                    plugin = self,
                    plugin_obj = card,
                    url = card.url,
                    status = status or None,
                    priority = priority,
                )]
                self.log.debug("Task created for card '%s'" % str(card.name))
            self.log.debug("Task list is %s" % str(tasks))
            result += [project.Project(
                name = board.name,
                pid = board.id,
                plugin = self,
                url = board.url,
                tasks = tasks
            )]
        self.log.debug("Boards loaded, returning %s" % str(result))
        return result

    def tasks(self, project = None):
        result = []
        if project:
            pass
        else:
            # Return all tasks
            pass
        return result

    def comments(self, task = None):
        """Get the comments for a task."""
        if task:
            card = task.plugin_obj
            comments = []
            start = timeit.default_timer()
            # card.fetch() # This isn't working with py-trello 1.6 since there is no due date
            self.log.debug("Fetching comments for %s..." % str(card))
            json_obj = card.client.fetch_json(
                           '/cards/' + card.id,
                           query_params={'badges': False}
                       )
            if json_obj['badges']['comments'] > 0:
                card.comments = card.client.fetch_json(
                                    '/cards/' + card.id + '/actions',
                                    query_params={'filter': 'commentCard'}
                                )

                self.log.debug("Loading comments for %s..." % str(card))
                most_recent = True # I think the first comment is always most recent
                # Comment JSON example
                # {
                #     u'type': u'commentCard',
                #     u'idMemberCreator': u'',
                #     u'memberCreator': {
                #         u'username': u'',
                #         u'fullName': u'',
                #         u'initials': u'',
                #         u'id': u'',
                #         u'avatarHash': None
                #     },
                #     u'date': u'2014-09-19T18:55:59.139Z',
                #     u'data': {
                #         u'text': u'',
                #         u'list': {
                #             u'name': u'',
                #             u'id': u''
                #         },
                #         u'board': {
                #             u'id': u'',
                #             u'name': u'',
                #             u'shortLink': u''
                #         },
                #         u'card': {
                #             u'idShort': int,
                #             u'id': u'',
                #             u'name': u'',
                #             u'shortLink': u''
                #         }
                #     }, u'id': u''
                # }
                for c in card.comments:
                    self.log.debug("Comment JSON is %s" % str(c))
                    comments += [comment.Comment(
                        name = c['data']['text'],
                        plugin = self,
                        url = None,
                        timestamp = datetime.strptime(
                            c['date'][:-5],
                            '%Y-%m-%dT%H:%M:%S',
                        ),
                        commentor = c['memberCreator']['fullName'],
                        most_recent = most_recent,
                    )]
                    most_recent = False
            self.log.debug("Comments loaded as %s" % str(comments))
            self.log.info("Comments loaded in %s" % str(timeit.default_timer() - start))
            return comments
        return None

    def complete(self, task = None):
        if task and task.plugin is self and task.plugin_obj:
            self.log.debug("Marking task %s as complete..." % str(task))
            card = task.plugin_obj

            # Find the list for completed tasks
            start = timeit.default_timer()
            complete_list_obj = None
            board = card.trello_list # Apparently this is a reference to the board
                                     # Likely since in projects() we did board.open_cards()
            lists = board.open_lists()
            for board_list in lists:
                if self.config['trello']['status'][board_list.name] == 'complete':
                    self.log.debug("Found list %s is the list for completed tasks" % str(board_list.name))
                    complete_list_obj = board_list
                    break
            # Move the card to the completed list
            self.log.debug("Moving card %s to list %s" % (str(card),str(complete_list_obj.name)))
            card.change_list(complete_list_obj.id)
            self.log.info("Task %s marked as complete in %s" % (
                str(task),
                str(timeit.default_timer() - start),
            ))

    def add_comment(self, task, text):
        if task.plugin is self and task.plugin_obj:
            self.log.info("Adding comment to %s..." % str(task))
            start = timeit.default_timer()
            task.plugin_obj.comment(text)
            self.log.info("Comment %s added in %s" % (
                str(text)[20:],
                str(timeit.default_timer() - start),
            ))
