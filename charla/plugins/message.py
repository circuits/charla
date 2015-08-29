from itertools import chain


from six import u

from circuits import handler

from circuits.protocols.irc import reply
from circuits.protocols.irc import Message as _Message

from circuits.protocols.irc.replies import ERR_CANNOTSENDTOCHAN, RPL_AWAY
from circuits.protocols.irc.replies import ERR_NOSUCHNICK, ERR_NOSUCHCHANNEL


from ..plugin import BasePlugin
from ..models import Channel, User
from ..commands import BaseCommands


class Commands(BaseCommands):

    def _channel_message(self, event, sock, source, target, message):
        user = User.objects.filter(sock=sock).first()

        channel = Channel.objects.filter(name=target).first()
        if channel is None:
            return ERR_NOSUCHCHANNEL(target)

        if u("n") in channel.modes:
            if not user.oper and user not in channel.users:
                return ERR_CANNOTSENDTOCHAN(channel.name)

        if u("m") in channel.modes:
            if not user.oper and user not in chain(channel.operators, channel.voiced):
                return ERR_CANNOTSENDTOCHAN(channel.name)

        self.notify(
            channel.users,
            _Message(event.name.upper(), target, message, prefix=user.prefix),
            user
        )

    def _user_message(self, event, sock, source, target, message):
        user = User.objects.filter(sock=sock).first()

        nick = User.objects.filter(nick=target).first()
        if nick is None:
            return ERR_NOSUCHNICK(target)

        self.fire(
            reply(
                nick.sock,
                _Message(event.name.upper(), nick.nick, message, prefix=user.prefix)
            ),
            "server"
        )

        if nick.away:
            return RPL_AWAY(nick.nick, nick.away)

    @handler("privmsg", "notice")
    def on_privmsg_or_notice(self, event, sock, source, target, message):
        if target and target[0] in (u("&"), u("#"),):
            return self._channel_message(event, sock, source, target, message)

        return self._user_message(event, sock, source, target, message)


class Message(BasePlugin):

    def init(self, *args, **kwargs):
        super(Message, self).init(*args, **kwargs)

        Commands(*args, **kwargs).register(self)
