from circuits import handler

from circuits.protocols.irc import joinprefix, reply, Message

from circuits.protocols.irc.replies import ERR_NOSUCHNICK, ERR_NOSUCHCHANNEL


from ..plugin import BasePlugin
from ..models import Channel, User
from ..commands import BaseCommands


class Commands(BaseCommands):

    @handler("privmsg", "notice")
    def on_privmsg_or_notice(self, event, sock, source, target, message):
        user = User.objects.filter(sock=sock).first()

        prefix = user.prefix or joinprefix(*source)

        if target.startswith("#"):
            channel = Channel.objects.filter(name=target).first()
            if channel is None:
                return ERR_NOSUCHCHANNEL(target)

            self.notify(
                channel.users,
                Message("PRIVMSG", target, message, prefix=prefix),
                user
            )
        else:
            user = User.objects.filter(nick=target).first()
            if user is None:
                return ERR_NOSUCHNICK(target)

            return reply(
                user.sock,
                Message(
                    event.name.upper(), target, message,
                    prefix=prefix
                )
            )


class MessagePlugin(BasePlugin):
    """Message Plugin"""

    __version__ = "0.0.1"
    __author__ = "James Mills, prologic at shortcircuit dot net dot au"

    def init(self, *args, **kwargs):
        super(MessagePlugin, self).init(*args, **kwargs)

        Commands(*args, **kwargs).register(self)
