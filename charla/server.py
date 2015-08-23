"""Server Module

Main Listening Server Component
"""


from datetime import datetime
from socket import has_ipv6
from logging import getLogger
from collections import defaultdict


from circuits import Component

from circuits.net.sockets import TCPServer, TCP6Server

from circuits.protocols.irc import response, IRC


from .models import User
from . import __name__, __url__, __version__


class Server(Component):

    channel = "server"

    network = "Test"
    host = "localhost"
    created = datetime.utcnow()

    features = (
        "PREFIX=(ov)@+",
        "CHANTYPES=#&",
    )

    url = __url__
    name = __name__
    version = __version__

    def init(self, config, db):
        self.config = config
        self.db = db

        self.logger = getLogger(__name__)

        self.buffers = defaultdict(bytes)

        port = config["port"]

        if has_ipv6:
            address = "::"
            Transport = TCP6Server
        else:
            address = "0.0.0.0"
            Transport = TCPServer

        bind = (address, port)

        self.transport = Transport(
            bind,
            channel=self.channel
        ).register(self)

        self.protocol = IRC(
            channel=self.channel,
            getBuffer=self.buffers.__getitem__,
            updateBuffer=self.buffers.__setitem__
        ).register(self)

    def ready(self, server, bind):
        self.logger.info(
            "{0} v{1} ready! Listening on: {1}\n".format(
                self.name, self.version, "{0}:{1}".format(*bind)
            )
        )

    def connect(self, sock, *args):
        host, port = args[:2]
        user = User(sock=sock, host=host, port=port)
        user.save()

    def disconnect(self, sock):
        user = User.objects.filter(sock=sock).first()
        if user is None:
            return

        nick = user.nick
        user, host = user.userinfo.user, user.userinfo.host

        quit = response.create("quit", sock, (nick, user, host), "Leavling")
        quit.complete = True
        quit.complete_channels = ("server",)

        self.fire(quit)
