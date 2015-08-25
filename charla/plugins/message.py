from circuits import handler

from circuits.protocols.irc import joinprefix, reply
from circuits.protocols.irc import Message as _Message

from circuits.protocols.irc.replies import ERR_NOSUCHNICK, ERR_NOSUCHCHANNEL


from ..plugin import BasePlugin
from ..models import Channel, User
from ..commands import BaseCommands
from ..replies import ERR_CANNOTSENDTOCHAN


class Commands(BaseCommands):

    @handler("privmsg", "notice")
    def on_privmsg_or_notice(self, event, sock, source, target, message):
        user = User.objects.filter(sock=sock).first()

        prefix = user.prefix or joinprefix(*source)

        if target.startswith(u"#"):
            channel = Channel.objects.filter(name=target).first()
            if channel is None:
                return ERR_NOSUCHCHANNEL(target)

            if "n" in channel.modes and user not in channel.users:
                return ERR_CANNOTSENDTOCHAN(channel.name)

            self.notify(
                channel.users,
                _Message(u"PRIVMSG", target, message, prefix=prefix),
                user
            )
        else:
            user = User.objects.filter(nick=target).first()
            if user is None:
                return ERR_NOSUCHNICK(target)

            return reply(
                user.sock,
                _Message(
                    event.name.upper(), target, message,
                    prefix=prefix
                )
            )


class Message(BasePlugin):

    def init(self, *args, **kwargs):
        super(Message, self).init(*args, **kwargs)

        Commands(*args, **kwargs).register(self)
