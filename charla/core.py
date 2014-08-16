# Module:   core
# Date:     16th August 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Core Module

Crates server and data components, loads plugins and handles process signals.
"""


from logging import getLogger
from signal import SIGINT, SIGHUP, SIGTERM


from circuits import handler, BaseComponent, Timer

from circuits.protocols.irc import Message

from .data import Data
from .server import Server
from .plugins import Plugins
from .events import broadcast, terminate


class Core(BaseComponent):

    channel = "core"

    def init(self, config):
        self.config = config

        self.data = Data()

        self.logger = getLogger(__name__)

        self.server = Server(self.config, self.data).register(self)

        self.plugins = Plugins(
            init_args=(self.server, self.config, self.data)
        ).register(self)

        self.logger.info("Loading plugins...")
        for plugin in self.config["plugins"]:
            self.plugins.load(plugin)

    @handler("signal", channel="*")
    def signal(self, signo, stack):
        if signo == SIGHUP:
            self.config.reload_config()
        elif signo in (SIGINT, SIGTERM):
            Timer(5, terminate()).register(self)
            self.fire(
                broadcast(
                    self.data.users.values(),
                    Message("NOTICE", "Received SIGTERM, terminating...")
                ),
                self.server
            )
        return True

    @handler("terminate")
    def terminate(self):
        raise SystemExit(0)
