# Plugin:   core
# Date:     16th August 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Core Plugin"""


__version__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from operator import attrgetter
from itertools import chain, imap


from circuits import handler

from circuits.net.events import close

from circuits.protocols.irc import reply, Message

from circuits.protocols.irc.replies import (
    RPL_WHOREPLY, RPL_ENDOFWHO, RPL_NOTOPIC, RPL_NAMEREPLY, RPL_ENDOFNAMES,
    ERR_NOSUCHNICK, ERR_NOSUCHCHANNEL, ERR_NICKNAMEINUSE,
)


from ..plugin import BasePlugin
from ..commands import BaseCommands
from ..events import broadcast, signon
from ..models import Channel, UserInfo


class Commands(BaseCommands):

    def quit(self, sock, source, reason="Leaving"):
        user = self.data.users[sock]

        for channel in user.channels:
            channel.users.remove(user)

            if not channel.users:
                del self.data.channels[channel.name]

        users = chain(*map(attrgetter("users"), user.channels))

        self.fire(close(sock), "server")

        msg = Message("QUIT", reason, prefix=user.prefix)
        self.fire(broadcast(users, msg, user), "server")

    def nick(self, sock, source, nick):
        user = self.data.users[sock]

        if nick in imap(attrgetter("nick"), self.data.users.itervalues()):
            return self.fire(reply(sock, ERR_NICKNAMEINUSE(nick)), "server")

        if not user.registered and user.userinfo:
            user.registered = True
            self.fire(signon(sock, source), "server")

        user.nick = nick

    def user(self, sock, source, user, host, server, name):
        _user = self.data.users[sock]

        _user.userinfo = UserInfo(user, host, server, name)

        if not _user.registered and _user.nick:
            _user.registered = True
            self.fire(signon(sock, source), "server")

    def join(self, sock, source, name):
        user = self.data.users[sock]

        if name in self.data.channels:
            channel = self.data.channels[name]
        else:
            channel = self.data.channels[name] = Channel(name)

        if user in channel.users:
            return

        self.fire(
            broadcast(
                channel.users[:],
                Message("JOIN", name, prefix=user.prefix)
            ),
            "server"
        )

        self.fire(
            reply(sock, Message("JOIN", name, prefix=user.prefix)),
            "server"
        )

        channel.users.append(user)

        user.channels.append(channel)

        self.fire(reply(sock, RPL_NOTOPIC(name)), "server")
        self.fire(reply(sock, RPL_NAMEREPLY(channel)), "server")
        self.fire(reply(sock, RPL_ENDOFNAMES()), "server")

    def part(self, sock, source, name, reason="Leaving"):
        user = self.data.users[sock]

        channel = self.data.channels.get(name)

        if channel is None:
            return

        if user not in channel.users:
            return

        self.fire(
            broadcast(
                channel.users,
                Message("PART", name, reason, prefix=user.prefix)
            ),
            "server"
        )

        user.channels.remove(channel)
        channel.users.remove(user)

        if not channel.users:
            del self.data.channels[name]

    @handler("privmsg", "notice")
    def on_privmsg_or_notice(self, event, sock, source, target, message):
        user = self.data.users[sock]

        if target.startswith("#"):
            channel = self.data.channels.get(target)
            if channel is None:
                return self.fire(
                    reply(sock, ERR_NOSUCHCHANNEL(target)),
                    "server"
                )

            self.fire(
                broadcast(
                    channel.users,
                    Message("PRIVMSG", target, message, prefix=user.prefix),
                    user
                ),
                "server"
            )
        else:
            user = self.data.users.get(target)
            if user is None:
                return self.fire(reply(sock, ERR_NOSUCHNICK(target)), "server")

            self.fire(
                reply(
                    user.sock,
                    Message(
                        event.name.uppwer(), target, message,
                        prefix=user.prefix
                    )
                )
            )

    def who(self, sock, source, mask):
        if mask.startswith("#"):
            channel = self.data.channels.get(mask)
            if channel is None:
                return self.fire(
                    reply(sock, ERR_NOSUCHCHANNEL(mask)),
                    "server"
                )

            for user in channel.users:
                self.fire(
                    reply(
                        sock,
                        RPL_WHOREPLY(user, mask, self.parent.server.host)
                    ),
                    "server"
                )
            self.fire(reply(sock, RPL_ENDOFWHO(mask)), "server")
        else:
            user = self.data.users.get(mask)
            if user is None:
                return self.fire(reply(sock, ERR_NOSUCHNICK(mask)), "server")

            self.fire(
                reply(
                    sock,
                    RPL_WHOREPLY(user, mask, self.parent.server.host)
                ),
                "server"
            )

            self.fire(reply(sock, RPL_ENDOFWHO(mask)), "server")


class Core(BasePlugin):
    """Core Plugin"""

    def init(self, *args, **kwargs):
        super(Core, self).init(*args, **kwargs)

        Commands(*args, **kwargs).register(self)
