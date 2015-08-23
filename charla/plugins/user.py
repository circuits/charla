# Plugin:   user
# Date:     16th August 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""User Plugin"""


__version__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from circuits.protocols.irc.replies import (
    ERR_NOSUCHNICK, ERR_NOSUCHCHANNEL,
    RPL_WHOREPLY, RPL_ENDOFWHO,
)


from ..plugin import BasePlugin
from ..models import Channel, User
from ..commands import BaseCommands


class Commands(BaseCommands):

    def who(self, sock, source, mask):
        if mask.startswith("#"):
            channel = Channel.objects.filter(name=mask).first()
            if channel is None:
                return ERR_NOSUCHCHANNEL(mask)

            return [
                RPL_WHOREPLY(user, mask, self.parent.server.host)
                for user in channel.users
            ] + [RPL_ENDOFWHO(mask)]
        else:
            user = User.objects.filter(nick=mask).first()
            if user is None:
                return ERR_NOSUCHNICK(mask)

            return (
                RPL_WHOREPLY(user, mask, self.parent.server.host),
                RPL_ENDOFWHO(mask)
            )


class UserPlugin(BasePlugin):
    """User Plugin"""

    def init(self, *args, **kwargs):
        super(UserPlugin, self).init(*args, **kwargs)

        Commands(*args, **kwargs).register(self)
