import asyncio
import argparse
import copy
import sys
import logging

# Install asyncio loop integration with tornado
from tornado.platform.asyncio import AsyncIOMainLoop
AsyncIOMainLoop().install()

from tornado.web import Application
from .handlers import EventsHandler
from .adapter import adapt_handler


DEFAULT_CONFIG = {
    "debug": True,
    "queue_conf": None,
    "repo_conf": None,
}


def make_app(config:dict) -> Application:
    handlers = [
       (r"/events", adapt_handler(EventsHandler), {"config": config}),
    ]
    return Application(handlers, debug=config["debug"])


def start_app(application:Application, *, port:int=8888, join:bool=True):
    application.listen(port)
    print("Now listening on: http://127.0.0.1:{0}".format(port), file=sys.stderr)

    if join:
        try:
            loop = asyncio.get_event_loop()
            loop.run_forever()
        except KeyboardInterrupt:
            loop.stop()


def parse_config_file(path:str) -> dict:
    """
    Given a path to a config file return a parsed
    configuration as python dict.

    A configuration file consists in a simple python
    file containing global variables.
    """

    with open(path) as f:
        module = copy.copy(DEFAULT_CONFIG)
        exec(f.read(), {}, module)
        return module


def validate_config(config:dict) -> (bool, str):
    if not config.get("repo_conf", None):
        return False, "Repo configuration is empty"

    if not config.get("queue_conf", None):
        return False, "Queue configuration is empty"

    return True, None


def apply_args_to_config(config:dict, args) -> dict:
    config = copy.deepcopy(config)

    if args.tornado_debug is not None:
        config["debug"] = args.tornado_debug

    return config


def main():
    parser = argparse.ArgumentParser(description='Taiga.io events-consumer gateway.')
    parser.add_argument("-p", "--port", dest="port", action="store", type=int,
                        default=8888, help="Set custom port number.")
    parser.add_argument("-l", "--log-level", dest="loglevel", action="store",
                        default="error", help="Set loglevel.")
    parser.add_argument("-t", "--tornado-debug", dest="tornado_debug", action="store_true",
                        default=None, help="Run with debug mode activeted on tornado app.")
    parser.add_argument("-f", "--config", dest="configfile", action="store",
                        help="Read configuration from python config file", required=True)

    args = parser.parse_args()
    config = parse_config_file(args.configfile)
    ok, msg = validate_config(config)

    if not ok:
        print(msg, file=sys.stderr)
        return -1

    logging.basicConfig(format="%(levelname)s %(name)s %(asctime)-15s %(message)s")
    logger = logging.getLogger("taiga")

    if args.loglevel == "error":
        logger.setLevel(logging.ERROR)
    elif args.loglevel == "warning":
        logger.setLevel(logging.WARNING)
    elif args.loglevel == "info":
        logger.setLevel(logging.INFO)
    elif args.loglevel == "debug":
        logger.setLevel(logging.DEBUG)
    else:
        print("Wrong log level: {0}".format(args.loglevel), file=sys.stderr)
        return -1

    app = make_app(apply_args_to_config(config, args))
    return start_app(app, port=args.port)
