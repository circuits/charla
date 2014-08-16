# Plugin:   user
# Date:     16th August 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""User Plugin"""


__version__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from circuits.protocols.irc import reply

from circuits.protocols.irc.replies import (
    ERR_NOSUCHNICK, ERR_NOSUCHCHANNEL,
    RPL_WHOREPLY, RPL_ENDOFWHO,
)


from ..plugin import BasePlugin
from ..commands import BaseCommands


class Commands(BaseCommands):

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


class UserPlugin(BasePlugin):
    """User Plugin"""

    def init(self, *args, **kwargs):
        super(UserPlugin, self).init(*args, **kwargs)

        Commands(*args, **kwargs).register(self)
