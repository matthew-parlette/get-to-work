from plugin import PluginProvider
from trello import TrelloClient, util
from entities import *

class Trello(PluginProvider):
    """docstring for Trello"""
    def __init__(self, log, config):
        super(Trello, self).__init__(log, config)
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
                for board_list in lists:
                    if board_list.id == card.list_id:
                        status = board_list.name
                        self.log.debug("Status for '%s' read as %s" % (str(card.name),str(status)))
                        break
                tasks += [task.Task(
                    name = card.name,
                    source = 'trello',
                    url = card.url,
                    status = status or None,
                )]
                self.log.debug("Task created for card '%s'" % str(card.name))
            self.log.debug("Task list is %s" % str(tasks))
            result += [project.Project(
                name = board.name,
                source = 'trello',
                url = board.url,
                tasks = tasks
            )]
        self.log.debug("Boards loaded, returning %s" % str(result))
        return result
