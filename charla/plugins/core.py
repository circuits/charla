# Plugin:   core
# Date:     16th August 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Core Plugin"""


__version__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from itertools import chain
from operator import attrgetter


from circuits.protocols.irc import joinprefix, Message

from circuits.protocols.irc.replies import ERR_NICKNAMEINUSE


from ..events import signon
from ..plugin import BasePlugin
from ..models import User, UserInfo
from ..commands import BaseCommands


class Commands(BaseCommands):

    def quit(self, sock, source, reason="Leaving"):
        user = User.objects(sock=sock).first()

        for channel in user.channels:
            channel.users.remove(user)

            if not channel.users:
                channel.delete()

        users = chain(*map(attrgetter("users"), user.channels))

        self.disconnect(user)

        self.notify(users, Message("QUIT", reason, prefix=user.prefix), user)

    def nick(self, sock, source, nick):
        user = User.objects(sock=sock).first()

        if User.objects.filter(nick=nick):
            return ERR_NICKNAMEINUSE(nick)

        prefix = user.prefix or joinprefix(*source)
        user.nick = nick
        user.save()

        if not user.registered and user.userinfo:
            user.registered = True
            user.save()
            return signon(sock, source)

        users = chain(*map(attrgetter("users"), user.channels))

        self.notify(users, Message("NICK", nick, prefix=prefix))

    def user(self, sock, source, username, hostname, server, realname):
        _user = User.objects(sock=sock).first()

        _user.userinfo = UserInfo(
            user=username, host=hostname, name=realname, server=server
        )

        _user.save()

        if not _user.registered and _user.nick:
            _user.registered = True
            _user.save()
            return signon(sock, source)


class CorePlugin(BasePlugin):
    """Core Plugin"""

    def init(self, *args, **kwargs):
        super(CorePlugin, self).init(*args, **kwargs)

        Commands(*args, **kwargs).register(self)
