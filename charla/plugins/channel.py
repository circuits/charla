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


from ..plugin import BasePlugin
from ..models import Channel, User
from ..commands import BaseCommands


class Commands(BaseCommands):

    def join(self, sock, source, name):
        user = User.objects.filter(sock=sock).first()

        channel = Channel.objects.filter(name=name).first()
        if channel is None:
            channel = Channel(name=name)
            channel.save()

        if user in channel.users:
            return

        self.notify(
            channel.users[:],
            Message("JOIN", name, prefix=user.prefix)
        )

        user.channels.append(channel)
        user.save()

        channel.users.append(user)
        channel.save()

        return (
            Message("JOIN", name, prefix=user.prefix),
            RPL_NOTOPIC(name),
            RPL_NAMEREPLY(channel),
            RPL_ENDOFNAMES()
        )

    def part(self, sock, source, name, reason="Leaving"):
        user = User.objects.filter(sock=sock).first()

        channel = Channel.objects.filter(name=name).first()

        if channel is None:
            return

        if user not in channel.users:
            return

        self.notify(
            channel.users,
            Message("PART", name, reason, prefix=user.prefix)
        )

        user.channels.remove(channel)
        user.save()

        channel.users.remove(user)
        channel.save()

        if not channel.users:
            channel.delete()


class ChannelPlugin(BasePlugin):
    """Channel Plugin"""

    def init(self, *args, **kwargs):
        super(ChannelPlugin, self).init(*args, **kwargs)

        Commands(*args, **kwargs).register(self)
