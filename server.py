#!/usr/bin/env python


"""IRC Daemon"""


from sys import stderr
from collections import defaultdict
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser


from circuits import handler, Component, Debugger

from circuits.net.events import write
from circuits.net.sockets import TCPServer

from circuits.protocols.irc import joinprefix, reply, response, IRC, Message

from circuits.protocols.irc.replies import (
    ERR_NOMOTD, ERR_NOSUCHNICK, ERR_NOSUCHCHANNEL, ERR_UNKNOWNCOMMAND,
    RPL_WELCOME, RPL_YOURHOST, RPL_WHOREPLY, RPL_ENDOFWHO, RPL_NOTOPIC,
    RPL_NAMEREPLY, RPL_ENDOFNAMES,
)


__version__ = "0.0.1"


def parse_args():
    parser = ArgumentParser(
        description=__doc__,
        formatter_class=ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version="%(prog)s {version}".format(version=__version__)
    )

    parser.add_argument(
        "-b", "--bind",
        action="store", type=str,
        default="0.0.0.0:6667", dest="bind",
        help="Bind to address:[port]"
    )

    parser.add_argument(
        "-d", "--debug",
        action="store_true",
        default=False, dest="debug",
        help="Enable debug mode"
    )

    return parser.parse_args()


class Server(Component):

    channel = "server"

    network = "Test"
    host = "localhost"
    version = "ircd v{0:s}".format(__version__)

    def init(self, args):
        self.args = args

        self.buffers = defaultdict(bytes)

        self.nicks = {}
        self.clients = {}
        self.channels = {}

        if args.debug:
            Debugger().register(self)

        if ":" in args.bind:
            address, port = args.bind.split(":")
            port = int(port)
        else:
            address, port = args.bind, 6667

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

    def read(self, sock, data):
        client = self.clients[sock]
        host, port = client["host"], client["port"]

        stderr.write("[{0:s}:{1:d}] -> {2:s}\n".format(host, port, repr(data)))

    def write(self, sock, data):
        client = self.clients[sock]
        host, port = client["host"], client["port"]

        stderr.write("[{0:s}:{1:d}] <- {2:s}\n".format(host, port, repr(data)))

    def ready(self, server, bind):
        stderr.write(
            "ircd v{0:s} ready! Listening on: {1:s}\n".format(
                __version__, "{0:s}:{1:d}".format(*bind)
            )
        )

    def connect(self, sock, host, port):
        self.clients[sock] = {
            "sock": sock,
            "host": host,
            "port": port,
            "nick": None,
            "away": False,
            "userinfo": {},
            "registered": False
        }

    def disconnect(self, sock):
        if sock not in self.clients:
            return

        client = self.clients[sock]

        del self.clients[sock]
        del self.nicks[client["nick"]]

    def nick(self, sock, source, nick):
        client = self.clients[sock]
        client["nick"] = nick
        self.nicks[nick] = client

    def user(self, sock, source, nick, user, host, name):
        client = self.clients[sock]

        client["userinfo"] = {
            "user": user,
            "host": host,
            "name": name
        }

        client["registered"] = True

        self.fire(reply(sock, RPL_WELCOME(self.network)))
        self.fire(reply(sock, RPL_YOURHOST(self.host, self.version)))
        self.fire(reply(sock, ERR_NOMOTD()))

    def join(self, sock, source, channel):
        client = self.clients[sock]

        if channel not in self.channels:
            channeldata = self.channels[channel] = {
                "name": channel,
                "users": []
            }
        else:
            channeldata = self.channels[channel]

        channeldata["users"].append(client)

        nick = client["nick"]
        userinfo = client["userinfo"]
        user, host = userinfo["user"], userinfo["host"]

        prefix = joinprefix(nick, user, host)

        for user in channeldata["users"]:
            self.fire(
                reply(
                    user["sock"],
                    Message("JOIN", channel, prefix=prefix)
                )
            )

        self.fire(reply(sock, RPL_NOTOPIC(channel)))
        self.fire(reply(sock, RPL_NAMEREPLY(channeldata)))
        self.fire(reply(sock, RPL_ENDOFNAMES()))

    def part(self, sock, source, channel, reason="Leaving"):
        client = self.clients[sock]

        channeldata = self.channels[channel]

        nick = client["nick"]
        userinfo = client["userinfo"]
        user, host = userinfo["user"], userinfo["host"]

        prefix = joinprefix(nick, user, host)

        for user in channeldata["users"]:
            self.fire(
                reply(
                    user["sock"],
                    Message("PART", channel, reason, prefix=prefix)
                )
            )

        channeldata["users"].remove(client)

        if not channeldata["users"]:
            del self.channels[channel]

    def privmsg(self, sock, source, target, message):
        client = self.clients[sock]

        nick = client["nick"]
        userinfo = client["userinfo"]
        user, host = userinfo["user"], userinfo["host"]

        prefix = joinprefix(nick, user, host)

        if target.startswith("#"):
            if target not in self.channels:
                return self.fire(reply(sock, ERR_NOSUCHCHANNEL(target)))

            channeldata = self.channels[target]
            for user in channeldata["users"]:
                if user is client:
                    continue

                self.fire(
                    reply(
                        user["sock"],
                        Message("PRIVMSG", target, message, prefix=prefix)
                    )
                )
        else:
            if target not in self.nicks:
                return self.fire(reply(sock, ERR_NOSUCHNICK(target)))

            user = self.nicks[target]

            self.fire(
                reply(
                    user["sock"],
                    Message("PRIVMSG", target, message, prefix=prefix)
                )
            )

    def who(self, sock, source, mask):
        if mask.startswith("#"):
            if mask not in self.channels:
                return self.fire(reply(sock, ERR_NOSUCHCHANNEL(mask)))

            channeldata = self.channels[mask]

            for user in channeldata["users"]:
                self.fire(reply(sock, RPL_WHOREPLY(user, mask, self.host)))
            self.fire(reply(sock, RPL_ENDOFWHO(mask)))
        else:
            if mask not in self.nicks:
                return self.fire(reply(sock, ERR_NOSUCHNICK(mask)))

            user = self.nicks[mask]

            self.fire(reply(sock, RPL_WHOREPLY(user, mask, self.host)))
            self.fire(reply(sock, RPL_ENDOFWHO(mask)))

    def ping(self, event, sock, source, server):
        event.stop()
        self.fire(reply(sock, Message("PONG", server)))

    def reply(self, target, message):
        client = self.clients[target]

        if message.add_nick:
            message.args.insert(0, client["nick"])

        if message.prefix is None:
            message.prefix = self.host

        self.fire(write(target, str(message)))

    @property
    def commands(self):
        exclude = {"ready", "connect", "disconnect", "read", "write"}
        return list(set(self.events()) - exclude)

    @handler()
    def _on_event(self, event, *args, **kwargs):
        if isinstance(event, response):
            if event.name not in self.commands:
                event.stop()
                self.fire(reply(args[0], ERR_UNKNOWNCOMMAND(event.name)))


def main():
    args = parse_args()

    Server(args).run()


if __name__ == "__main__":
    main()
