import re
from itertools import chain
from operator import attrgetter


from circuits.protocols.irc import joinprefix, Message
from circuits.protocols.irc.replies import ERR_ERRONEUSNICKNAME, ERR_NICKNAMEINUSE


from ..events import signon
from ..plugin import BasePlugin
from ..models import User, UserInfo
from ..commands import BaseCommands


VALID_NICK_REGEX = re.compile(r"^[][\`_^{|}A-Za-z][][\`_^{|}A-Za-z0-9-]*$")


class Commands(BaseCommands):

    def quit(self, sock, source, reason=u"Leaving", **kwargs):
        user = User.objects.filter(sock=sock).first()

        for channel in user.channels:
            channel.users.remove(user)

            if not channel.users:
                channel.delete()

        users = chain(*map(attrgetter("users"), user.channels))

        if kwargs.get("disconnect", True):
            self.disconnect(user)

        self.notify(users, Message(u"QUIT", reason, prefix=user.prefix), user)

    def nick(self, sock, source, nick):
        user = User.objects.filter(sock=sock).first()

        if not VALID_NICK_REGEX.match(nick):
            return ERR_ERRONEUSNICKNAME(nick)

        if len(nick) > self.parent.nicklen:
            return ERR_ERRONEUSNICKNAME(nick)

        if any(x for x in User.objects.all() if x.nick and x.nick.lower() == nick.lower()):
            return ERR_NICKNAMEINUSE(nick)

        prefix = user.prefix or joinprefix(*source)
        user.nick = nick
        user.save()

        if user.userinfo and user.userinfo.user is not None:
            user.registered = True
            user.save()
            return signon(sock, user.source)

        users = chain(*map(attrgetter("users"), user.channels))

        self.notify(users, Message(u"NICK", nick, prefix=prefix))

    def user(self, sock, source, username, unused1, unused2, realname):
        _user = User.objects.filter(sock=sock).first()

        if _user.userinfo is None:
            userinfo = UserInfo(user=username, name=realname, server=self.parent.server.host)
        else:
            userinfo = _user.userinfo
            userinfo.user = username
            userinfo.name = realname
            userinfo.server = self.parent.server.host

        userinfo.save()

        _user.userinfo = userinfo
        _user.save()

        if _user.nick is not None:
            _user.registered = True
            _user.save()
            return signon(sock, _user.source)


class Core(BasePlugin):

    def init(self, *args, **kwargs):
        super(Core, self).init(*args, **kwargs)

        self.nicklen = 16

        self.features = (
            "NICKLEN={0}".format(self.nicklen),
        )

        Commands(*args, **kwargs).register(self)

    def supports(self):
        return self.features
