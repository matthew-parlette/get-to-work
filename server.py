#!/usr/bin/python

import argparse
import logging
import os
import yaml
import json
import tornado.web
import tornado.ioloop
import tornado.auth
from plugin import PluginMount, PluginProvider
from entities import *
import ui_modules
import timeit
import base64
import uuid

global log
global config
global plugins
cache = {
    'projects': {
        'items': [],
        'expires': None,
    },
    'tasks': {
        'items': [],
        'expires': None,
    },
}
menu_state = {
    'projects': False,
}

def merge(x,y):
    # store a copy of x, but overwrite with y's values where applicable
    merged = dict(x,**y)

    xkeys = x.keys()

    # if the value of merged[key] was overwritten with y[key]'s value
    # then we need to put back any missing x[key] values
    for key in xkeys:
        # if this key is a dictionary, recurse
        if isinstance(x[key],dict) and y.has_key(key):
            merged[key] = merge(x[key],y[key])

    return merged

def refresh_cache():
    global cache
    # Update everything for now

    # Refresh projects
    start = timeit.default_timer()
    projects = []
    for plugin in plugins:
        projects += plugin.projects()
    log.debug("Projects loaded as %s" % str(projects))
    log.info("Projects loaded in %s" % str(timeit.default_timer() - start))
    cache['projects'] = {
        'items': projects,
        'expires': None,
    }

    # Refresh tasks
    start = timeit.default_timer()
    tasks = []
    for plugin in plugins:
        tasks += plugin.tasks()
    log.debug("Tasks loaded as %s" % str(tasks))
    log.info("Tasks loaded in %s" % str(timeit.default_timer() - start))
    cache['tasks'] = {
        'items': tasks,
        'expires': None,
    }

    # Return cache
    return cache

def get_projects():
    """Deprecated, use refresh_cache() instead"""
    refresh_cache()
    return cache['projects']['items']

def get_tasks():
    """Deprecated, use refresh_cache() instead"""
    refresh_cache()
    return cache['tasks']['items']

def find_task(tid):
    log.info("Looking for task %s" % str(tid))
    projects = get_projects()
    for project in projects:
        for task in project.tasks:
            if task.id == tid:
                log.info("Found task: %s" % str(task))
                return task
    log.warning("Task not found: %s" % str(tid))
    return None

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        self.user = self.get_secure_cookie("user")
        if not self.user:
            return None # @torando.web.authenticated will redirect to login_url
        log.info("User loaded as %s" % str(self.user))

class AuthHandler(BaseHandler, tornado.auth.GoogleOAuth2Mixin):
    @tornado.gen.coroutine
    def get(self):
        if self.get_argument("code", False):
            user = yield self.get_authenticated_user(
                redirect_uri='http://localhost:8010/login',
                code=self.get_argument('code'),
            )
            self.set_secure_cookie("user", tornado.escape.json_encode(user))
        yield self.authorize_redirect(
            redirect_uri='http://localhost:8010/login',
            client_id=self.settings['google_oauth']['key'],
            scope=[
                'email',
            ],
            response_type='code',
            extra_params={'approval_prompt': 'auto'},
        )

    def _on_auth(self, user):
        if not user:
            self.send_error(500)
        self.set_secure_cookie("user", tornado.escape.json_encode(user))
        self.redirect("/")

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        projects = get_projects()
        self.render(
            "templates/index.html",
            config = config,
            menu_state = menu_state,
            projects = cache['projects']['items'],
            tasks = cache['tasks']['items'],
        )

class ProjectHandler(BaseHandler):
    def get(self, pid):
        projects = get_projects()
        menu_state['projects'] = True
        self.render(
            "templates/project.html",
            config = config,
            menu_state = menu_state,
            projects = cache['projects']['items'],
            tasks = cache['tasks']['items'],
            pid = pid,
        )

class TaskHandler(BaseHandler):
    def get(self, tid = None, action = None):
        log.info("Received %s as GET" % (str(self.request)))
        if tid:
            task = find_task(tid)
            if task:
                self.render(
                    "templates/components/task.html",
                    config = config,
                    task = task,
                )
        else:
            # Show all tasks
            tasks = get_tasks()
            projects = get_projects()
            if tasks:
                self.render(
                    "templates/task.html",
                    config = config,
                    menu_state = menu_state,
                    projects = cache['projects']['items'],
                    tasks = cache['tasks']['items'],
                )

    def post(self, tid, action = None):
        log.debug("Received %s as POST" % (str(self.request)))
        log.info("Action is %s" % str(action))
        projects = get_projects()
        if action and action in ['comment','close']:
            self.set_status(404) # Status: Not Found
            # Find the task being requested
            task = find_task(tid)
            if task:
                data = None
                if self.request.body:
                    log.debug("Loading JSON from request body of %s..." % str(self.request.body))
                    data = json.loads(self.request.body)

                if action == 'comment':
                    comment = data['comment'] if 'comment' in data else None
                    task.plugin.add_comment(task = task, text = comment)
                    self.set_status(200) # Status: OK
                elif action == 'close':
                    task.plugin.complete(task = task)
                    self.set_status(200) # Status: OK

                # Return the updated task
                self.render(
                    "templates/components/task.html",
                    config = config,
                    task = task,
                )

settings = {
    "static_path": os.path.join(os.path.dirname(__file__),'static'),
    "favicon_path": os.path.join(os.path.dirname(__file__),'static','favicon.ico'),
    "ui_modules": {
        'Project': ui_modules.Project,
        'Task': ui_modules.Task,
        'Comment': ui_modules.Comment,
    },
    "debug": True, # Automatically restarts when any code is changed
    "cookie_secret": "3ZjlSoiJ74RNSN4q1MBADQz8OGdcOTiF",
    "login_url": "/login",
    "google_oauth": {
        "key": "120093985192-8ut99ctto053ejn4eqapllaku47h0iuq.apps.googleusercontent.com",
        "secret": "G4kb5KktCBMJ8bKAO28gzXm3",
    },
}

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/login", AuthHandler),
    (r"/project/(.*)", ProjectHandler),
    (r"/task/(.*)/(comment|close)", TaskHandler),
    (r"/task/(.*)$", TaskHandler),
    (r"/task", TaskHandler),
], **settings)

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Process command line options.')
    parser.add_argument('-d','--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('-c','--config', help='Specify a config file to use',
                        type=str, default='config.yaml')
    parser.add_argument('--version', action='version', version='0')
    args = parser.parse_args()

    # Setup logging options
    global log
    log_level = logging.DEBUG if args.debug else logging.INFO
    log = logging.getLogger(os.path.basename(__file__))
    log.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(funcName)s(%(lineno)i):%(message)s')

    ## Console Logging
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    ch.setFormatter(formatter)
    log.addHandler(ch)

    ## File Logging
    fh = logging.FileHandler(os.path.basename(__file__) + '.log')
    fh.setLevel(log_level)
    fh.setFormatter(formatter)
    log.addHandler(fh)

    log.info("Initializing...")

    # Load Config
    global config
    defaults = {
        # "cookie_secret": base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
        "trello": {
            "key": "",
            "secret": "",
            "oauth_token": "",
            "oauth_token_secret": "",
            "status": {
                "today": "working",
                "short list": "shortlist",
                "backlog": "backlog",
                "done": "complete",
            },
            "priority": {
                "mild": "low",
                "medium": "medium",
                "hot": "high",
            },
        },
        "zendesk": {
            "url": "",
            "email": "",
            "password": "",
            "view": "", # view id to use when listing tickets
            "status": {
                "Open": "working",
                "Pending": "shortlist",
                "On-hold": "backlog",
                "Solved": "complete",
            },
            "priority": {
                "Low": "low",
                "Normal": "medium",
                "High": "high",
                "Urgent": "high",
            },
        },
    }
    if os.path.isfile(args.config):
        log.debug("Loading config file %s" % args.config)
        config = yaml.load(file(args.config))
        if config:
            # config contains items
            config = merge(defaults,yaml.load(file(args.config)))
            log.debug("Config merged with defaults")
        else:
            # config is empty, just use defaults
            config = defaults
            log.debug("Config file was empty, loaded config from defaults")
    else:
        log.debug("Config file does not exist, creating a default config...")
        config = defaults

    log.debug("Config loaded as:\n%s, saving this to disk" % str(config))
    with open(args.config, 'w') as outfile:
        outfile.write( yaml.dump(config, default_flow_style=False) )

    log.info("Loading plugins...")
    from plugins import *
    global plugins
    plugins = [p(log, config) for p in PluginProvider.plugins]
    log.info("Plugins loaded as %s" % str(plugins))

    log.info("Initialization complete")

    port = 8010
    log.info("Starting web server on port %s..." % str(port))
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()
