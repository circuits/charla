# Plugin:   core
# Date:     16th August 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Core Plugin"""


__version__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from operator import attrgetter
from itertools import chain, imap


from circuits.protocols.irc import Message

from circuits.protocols.irc.replies import ERR_NICKNAMEINUSE


from ..events import signon
from ..models import UserInfo
from ..plugin import BasePlugin
from ..commands import BaseCommands


class Commands(BaseCommands):

    def quit(self, sock, source, reason="Leaving"):
        user = self.data.users[sock]

        for channel in user.channels:
            channel.users.remove(user)

            if not channel.users:
                del self.data.channels[channel.name]

        users = chain(*map(attrgetter("users"), user.channels))

        self.disconnect(user)

        self.notify(users, Message("QUIT", reason, prefix=user.prefix), user)

    def nick(self, sock, source, nick):
        user = self.data.users[sock]

        if nick in imap(attrgetter("nick"), self.data.users.itervalues()):
            return ERR_NICKNAMEINUSE(nick)

        prefix = user.prefix
        user.nick = nick

        if not user.registered and user.userinfo:
            user.registered = True
            return signon(sock, source)

        users = chain(*map(attrgetter("users"), user.channels))

        self.notify(users, Message("NICK", nick, prefix=prefix))

    def user(self, sock, source, user, host, server, name):
        _user = self.data.users[sock]

        _user.userinfo = UserInfo(user, host, server, name)

        if not _user.registered and _user.nick:
            _user.registered = True
            return signon(sock, source)


class CorePlugin(BasePlugin):
    """Core Plugin"""

    def init(self, *args, **kwargs):
        super(CorePlugin, self).init(*args, **kwargs)

        Commands(*args, **kwargs).register(self)
