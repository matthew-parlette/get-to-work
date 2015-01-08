from plugin import PluginProvider
import zendesk
from entities import *
from datetime import datetime
import timeit

class Zendesk(PluginProvider):
    """docstring for Trello"""
    def __init__(self, log, config):
        super(Zendesk, self).__init__(log, config)
        self.name = 'zendesk' # Friendly name for this plugin source
        self.icon = 'ticket' # Font Awesome icon name
        self.log.info("Initializing Zendesk plugin...")
        self.api = zendesk.Zendesk(
            zendesk_url = self.config['zendesk']['url'],
            zendesk_username = self.config['zendesk']['email'],
            zendesk_password = self.config['zendesk']['password'],
            api_version = 2, # v1 is disabled permanently
        )
        self.log.info("Zendesk plugin initialized")

    def tasks(self, project = None):
        result = []

        view_id = self.config['zendesk']['view']
        self.log.info("Retrieving list of tickets from view %s..." % str(view_id))
        """execute_view return format:
        {
            'count': int,
            'organizations': [
                {
                    'url': '...',
                    'id': int,
                    'name': '...'
                }
            ],
            'next_page': None,
            'rows': [
                {
                    'status': 'Open',
                    'organization_id': int,
                    'created': '2015-01-06T14:29:09Z',
                    'fields': [],
                    'priority': 'Low',
                    'ticket_id': int,
                    'requester_id': int,
                    'group_id': int,
                    'type': 'Question',
                    'ticket': {
                        'status': 'open',
                        'description': "...",
                        'url': '...',
                        'last_comment': {
                            'body': "...",
                            'created_at': '2015-01-06T14:29:09Z',
                            'author_id': int,
                            'public': True
                        },
                        'priority': 'low',
                        'type': 'question',
                        'id': int,
                        'subject': '...'
                    },
                    'custom_fields': [],
                    'subject': '...'
                },
                {...}
            ]
        }
        """
        tickets = self.api.execute_view(view_id = view_id)
        self.log.debug("Tickets list is %s" % str(tickets))
        if tickets and tickets['count'] > 0:
            self.log.debug("Loading tickets as Tasks...")
            for ticket in tickets['rows']:
                result += [task.Task(
                    name = ticket['subject'],
                    id = ticket['ticket_id'],
                    plugin = self,
                    plugin_obj = ticket,
                    url = ticket['ticket']['url'],
                    status = self.config['zendesk']['status'][ticket['status']],
                    priority = self.config['zendesk']['priority'][ticket['priority']],
                    comments = [],
                    commentable = False,
                    closeable = False,
                )]

        return result
