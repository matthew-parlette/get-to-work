#!/usr/bin/python

import argparse
import logging
import os
import yaml
import tornado.web
import tornado.ioloop
from plugin import PluginMount, PluginProvider
from entities import *

global log
global config
global plugins

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        projects = []
        for plugin in plugins:
            projects += plugin.projects()
        log.info("Projects loaded as %s" % str(projects))
        self.render(
            "templates/index.html",
            config = config,
            projects = projects
        )

application = tornado.web.Application([
    (r"/", MainHandler),
], static_path=os.path.join(os.path.dirname(__file__),'static'))

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
            "lists": {
                "working": "today",
                "shortlist": "short list",
                "backlog": "backlog",
            }
        },
    }
    if os.path.isfile(args.config):
        log.debug("Loading config file %s" % args.config)
        config = yaml.load(file(args.config))
        if config:
            # config contains items
            config = dict(defaults.items() + yaml.load(file(args.config)).items())
        else:
            # config is empty, just use defaults
            config = defaults
        log.debug("Config file loaded, writing current config to file")
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
