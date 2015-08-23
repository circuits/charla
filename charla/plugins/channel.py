from circuits.protocols.irc import Message
from circuits.protocols.irc.replies import RPL_NOTOPIC, RPL_NAMEREPLY, RPL_ENDOFNAMES


from ..plugin import BasePlugin
from ..replies import MODE, JOIN
from ..models import Channel, User
from ..commands import BaseCommands


class Commands(BaseCommands):

    def join(self, sock, source, name):
        user = User.objects.filter(sock=sock).first()

        replies = [JOIN(name, prefix=user.prefix)]

        channel = Channel.objects.filter(name=name).first()
        if channel is None:
            channel = Channel(name=name)
            channel.save()

        if user in channel.users:
            return

        self.notify(
            channel.users[:],
            JOIN(name, prefix=user.prefix)
        )

        user.channels.append(channel)
        user.save()

        if not channel.users:
            replies.append(MODE(name, "+o {0}".format(user.nick), prefix=self.server.host))
            channel.operators.append(user)
            channel.save()

        channel.users.append(user)
        channel.save()

        replies.append(RPL_NOTOPIC(name))
        replies.append(RPL_NAMEREPLY(channel.name, channel.userprefixes))
        replies.append(RPL_ENDOFNAMES())

        return replies

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

    __version__ = "0.0.1"
    __author__ = "James Mills, prologic at shortcircuit dot net dot au"

    def init(self, *args, **kwargs):
        super(ChannelPlugin, self).init(*args, **kwargs)

        Commands(*args, **kwargs).register(self)
