"""Server Module

Main Listening Server Component
"""


from time import time
from datetime import datetime
from socket import has_ipv6
from logging import getLogger
from collections import defaultdict


from six import u

from pathlib import Path

from circuits import Event, Component, Timer

from circuits.protocols.irc import response, IRC

from circuits.net.sockets import TCPServer, TCP6Server


from .models import User
from . import __name__, __url__, __version__


def read_motd(filename, encoding="utf-8"):
    try:
        with Path("motd.txt").resolve().open("rb") as f:
            for line in f:
                yield line.decode(encoding).strip()
    except IOError:
        return


class setup(Event):
    """setup Event"""


class Server(Component):

    channel = "server"

    info = u("QLD, Australia")
    network = u("ShortCircuit")
    host = u("daisy.shortcircuit.net.au")
    created = datetime.utcnow()

    url = u(__url__)
    name = u(__name__)
    version = u(__version__)

    features = (
        u("NETWORK={0}").format(network),
    )

    def init(self, config, db):
        self.config = config
        self.db = db

        self.encoding = "utf-8"
        self.motd = list(read_motd(self.encoding))

        self.logger = getLogger(__name__)

        self.buffers = defaultdict(bytes)

        self.port = config["port"]

        if has_ipv6:
            self.address = "::"
            self.Transport = TCP6Server
        else:
            self.address = "0.0.0.0"
            self.Transport = TCPServer

        self.bind = (self.address, self.port)

        self.fire(setup())

    def setup(self):
        try:
            self.transport = self.Transport(
                self.bind,
                channel=self.channel
            ).register(self)

            self.protocol = IRC(
                channel=self.channel,
                getBuffer=self.buffers.__getitem__,
                updateBuffer=self.buffers.__setitem__
            ).register(self)
        except Exception as e:
            self.logger.error(u("Cannot start server: {0}").format(e))
            self.logger.info(u("Retrying in 5s ..."))
            Timer(5, setup()).register(self)

    def ready(self, server, bind):
        self.logger.info(
            u("{0} v{1} ready! Listening on: {2}\n").format(
                self.name, self.version, u("{0}:{1}").format(*bind)
            )
        )

    def connect(self, sock, *args):
        host, port = args[:2]
        user = User(sock=sock, host=host, port=port)
        user.lastmessage = int(time())
        user.save()

    def disconnect(self, sock):
        user = User.objects.filter(sock=sock).first()
        if user is None:
            return

        nick = user.nick
        user, host = user.userinfo.user, user.userinfo.host

        quit = response.create("quit", sock, (nick, user, host), u("Leaving"))
        quit.complete = True
        quit.complete_channels = ("server",)

        self.fire(quit)

    def supports(self):
        return self.features
