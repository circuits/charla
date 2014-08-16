# Plugin:   message
# Date:     16th August 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Message Plugin"""


__version__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from circuits import handler

from circuits.protocols.irc import reply, Message

from circuits.protocols.irc.replies import ERR_NOSUCHNICK, ERR_NOSUCHCHANNEL


from ..events import broadcast
from ..plugin import BasePlugin
from ..commands import BaseCommands


class Commands(BaseCommands):

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


class MessagePlugin(BasePlugin):
    """Message Plugin"""

    def init(self, *args, **kwargs):
        super(MessagePlugin, self).init(*args, **kwargs)

        Commands(*args, **kwargs).register(self)
