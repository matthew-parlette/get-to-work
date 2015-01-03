#!/usr/bin/python

import argparse
import logging
import os
import yaml
import tornado.web
import tornado.ioloop
from plugin import PluginMount, PluginProvider
from entities import *
import ui_modules

global log
global config
global plugins
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

def get_projects():
    projects = []
    for plugin in plugins:
        projects += plugin.projects()
    log.debug("Projects loaded as %s" % str(projects))
    return projects

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        projects = get_projects()
        self.render(
            "templates/index.html",
            config = config,
            menu_state = menu_state,
            projects = projects
        )

class ProjectHandler(tornado.web.RequestHandler):
    def get(self, pid):
        projects = get_projects()
        menu_state['projects'] = True
        self.render(
            "templates/project.html",
            config = config,
            menu_state = menu_state,
            projects = projects,
            pid = pid
        )

settings = {
    "static_path": os.path.join(os.path.dirname(__file__),'static'),
    "ui_modules": {
        'Project': ui_modules.Project,
        'Task': ui_modules.Task,
    },
}

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/project/(.*)", ProjectHandler),
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
