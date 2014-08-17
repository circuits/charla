# Plugin:   channel
# Date:     16th August 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Channel Plugin"""


__version__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from circuits.protocols.irc import Message

from circuits.protocols.irc.replies import (
    RPL_NOTOPIC, RPL_NAMEREPLY, RPL_ENDOFNAMES,
)


from ..models import Channel
from ..plugin import BasePlugin
from ..commands import BaseCommands


class Commands(BaseCommands):

    def join(self, sock, source, name):
        user = self.data.users[sock]

        if name in self.data.channels:
            channel = self.data.channels[name]
        else:
            channel = self.data.channels[name] = Channel(name)

        if user in channel.users:
            return

        self.notify(
            channel.users[:],
            Message("JOIN", name, prefix=user.prefix)
        )

        yield Message("JOIN", name, prefix=user.prefix)

        channel.users.append(user)

        user.channels.append(channel)

        yield RPL_NOTOPIC(name)
        yield RPL_NAMEREPLY(channel)
        yield RPL_ENDOFNAMES()

    def part(self, sock, source, name, reason="Leaving"):
        user = self.data.users[sock]

        channel = self.data.channels.get(name)

        if channel is None:
            return

        if user not in channel.users:
            return

        self.notify(
            channel.users,
            Message("PART", name, reason, prefix=user.prefix)
        )

        user.channels.remove(channel)
        channel.users.remove(user)

        if not channel.users:
            del self.data.channels[name]


class ChannelPlugin(BasePlugin):
    """Channel Plugin"""

    def init(self, *args, **kwargs):
        super(ChannelPlugin, self).init(*args, **kwargs)

        Commands(*args, **kwargs).register(self)
