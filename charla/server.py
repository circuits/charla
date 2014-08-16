# Module:   server
# Date:     16th August 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Server Module

Main Listening Server Component
"""


from sys import stderr
from logging import getLogger
from collections import defaultdict


from bidict import bidict
from cidict import cidict

from circuits import handler, Component

from circuits.net.events import write
from circuits.net.sockets import TCPServer

from circuits.protocols.irc import reply, response, IRC

from circuits.protocols.irc.replies import (
    ERR_NOMOTD, ERR_UNKNOWNCOMMAND,
    RPL_WELCOME, RPL_YOURHOST,
)


from .models import User
from .version import version
from .plugin import BasePlugin


class Server(Component):

    channel = "server"

    network = "Test"
    host = "localhost"
    version = "ircd v{0:s}".format(version)

    def init(self, config, data):
        self.config = config
        self.data = data

        self.logger = getLogger(__name__)

        # command -> plugin
        self.command = cidict()

        # plugin name -> commands
        self.commands = cidict()

        # plugin name -> plugin
        self.plugins = cidict()

        self.data.init({
            "users": bidict(),
            "channels": cidict(),
        })

        self.buffers = defaultdict(bytes)

        if ":" in config["bind"]:
            address, port = config["bind"].split(":")
            port = int(port)
        else:
            address, port = config["bind"], 6667

        bind = (address, port)

        self.transport = TCPServer(
            bind,
            channel=self.channel
        ).register(self)

        self.protocol = IRC(
            channel=self.channel,
            getBuffer=self.buffers.__getitem__,
            updateBuffer=self.buffers.__setitem__
        ).register(self)

    @handler("registered", channel="*")
    def _on_registered(self, component, manager):
        if component.channel == "commands":
            for event in component.events():
                if event not in self.command:
                    self.command[event] = component

            if component.parent.name in self.commands:
                events = self.commands[component.parent.name]
                events = events.union(component.events())
                self.commands[component.parent.name] = events
            else:
                self.commands[component.parent.name] = set(component.events())

        if isinstance(component, BasePlugin):
            if component.name not in self.plugins:
                self.plugins[component.name] = component

    @handler("unregistered", channel="*")
    def _on_unregistered(self, component, manager):
        if component.channel == "commands":
            for event in component.events():
                if event in self.command:
                    del self.command[event]

        if isinstance(component, BasePlugin):
            if component.name in self.commands:
                del self.commands[component.name]
            if component.name in self.plugins:
                del self.plugins[component.name]

    def ready(self, server, bind):
        self.logger.info(
            "ircd v{0:s} ready! Listening on: {1:s}\n".format(
                version, "{0:s}:{1:d}".format(*bind)
            )
        )

    def connect(self, sock, host, port):
        user = User(sock, host, port)

        self.data.users[sock] = user

        self.logger.info("C: [{0:s}:{1:d}]".format(host, port))

    def disconnect(self, sock):
        if sock not in self.data.users:
            return

        user = self.data.users[sock]

        self.logger.info("D: [{0:s}:{1:d}]".format(user.host, user.port))

        nick = user.nick
        user, host = user.userinfo.user, user.userinfo.host

        yield self.call(
            response.create("quit", sock, (nick, user, host), "Leavling")
        )

        user.delete()
        user.save()

    def read(self, sock, data):
        user = self.data.users[sock]

        host, port = user.host, user.port

        self.logger.info(
            "I: [{0:s}:{1:d}] {2:s}".format(host, port, repr(data))
        )

    def write(self, sock, data):
        user = self.data.users.get(sock, User(sock))

        host, port = user.host, user.port

        self.logger.info(
            "O: [{0:s}:{1:d}] {2:s}".format(host, port, repr(data))
        )

    def broadcast(self, users, message, *exclude):
        for user in users:
            if user in exclude:
                continue

            self.fire(reply(user.sock, message))

    def signon(self, sock, source):
        self.fire(reply(sock, RPL_WELCOME(self.network)))
        self.fire(reply(sock, RPL_YOURHOST(self.host, self.version)))
        self.fire(reply(sock, ERR_NOMOTD()))

        # Force users to join #circuits
        self.fire(response.create("join", sock, source, "#circuits"))

    def reply(self, sock, message):
        user = self.data.users[sock]

        if message.add_nick:
            message.args.insert(0, user.nick or "")

        if message.prefix is None:
            message.prefix = self.host

        self.fire(write(sock, bytes(message)))

    @handler()
    def _on_event(self, event, *args, **kwargs):
        if event.name.endswith("_done"):
            return

        if isinstance(event, response):
            sock = args[0]
            if event.name not in self.command:
                event.stop()
                return self.fire(reply(sock, ERR_UNKNOWNCOMMAND(event.name)))

            self.fire(event, "commands")
