# Plugin:   connection
# Date:     16th August 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Connection Plugin"""


__version__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from operator import attrgetter
from itertools import chain, imap


from circuits.net.events import close

from circuits.protocols.irc import reply, Message

from circuits.protocols.irc.replies import ERR_NICKNAMEINUSE


from ..models import UserInfo
from ..plugin import BasePlugin
from ..commands import BaseCommands
from ..events import broadcast, signon


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


class CorePlugin(BasePlugin):
    """Core Plugin"""

    def init(self, *args, **kwargs):
        super(CorePlugin, self).init(*args, **kwargs)

        Commands(*args, **kwargs).register(self)
