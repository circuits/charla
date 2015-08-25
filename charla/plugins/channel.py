import re


from circuits.protocols.irc import Message


from .. import models
from ..plugin import BasePlugin
from ..commands import BaseCommands
from ..replies import MODE, JOIN, TOPIC
from ..replies import RPL_NAMEREPLY, RPL_ENDOFNAMES, ERR_CHANOPRIVSNEEDED
from ..replies import RPL_NOTOPIC, RPL_TOPIC, ERR_NOSUCHCHANNEL, ERR_TOOMANYCHANNELS


VALID_CHANNEL_REGEX = re.compile(r"^[&#+!][^\x00\x07\x0a\x0d ,:]*$")


class Commands(BaseCommands):

    def join(self, sock, source, name):
        user = models.User.objects.filter(sock=sock).first()

        if name and name[0] not in self.parent.chantypes:
            return ERR_NOSUCHCHANNEL(name)

        if VALID_CHANNEL_REGEX.match(name) is None:
            return ERR_NOSUCHCHANNEL(name)

        if len(name) > self.parent.channellen:
            return ERR_NOSUCHCHANNEL(name)

        replies = [JOIN(name, prefix=user.prefix)]

        channel = models.Channel.objects.filter(name=name).first()
        if channel is None:
            channel = models.Channel(name=name)
            channel.save()

        if user in channel.users:
            return

        type = name[0]
        nchannels = len([x for x in user.channels if channel.type == type])
        if nchannels >= self.parent.chanlimit[type]:
            return ERR_TOOMANYCHANNELS(name)

        self.notify(
            channel.users[:],
            JOIN(name, prefix=user.prefix)
        )

        user.channels.append(channel)
        user.save()

        if not channel.users:
            replies.append(MODE(name, u"+o {0}".format(user.nick), prefix=self.server.host))
            channel.operators.append(user)
            channel.save()

        channel.users.append(user)
        channel.save()

        replies.append(RPL_NOTOPIC(name))
        replies.append(RPL_NAMEREPLY(channel.name, channel.userprefixes))
        replies.append(RPL_ENDOFNAMES(name))

        return replies

    def part(self, sock, source, name, reason=u"Leaving"):
        user = models.User.objects.filter(sock=sock).first()

        channel = models.Channel.objects.filter(name=name).first()

        if channel is None:
            return

        if user not in channel.users:
            return

        self.notify(
            channel.users,
            Message(u"PART", name, reason, prefix=user.prefix)
        )

        user.channels.remove(channel)
        user.save()

        channel.users.remove(user)
        channel.save()

        if not channel.users:
            channel.delete()

    def topic(self, sock, source, name, topic=None):
        user = models.User.objects.filter(sock=sock).first()

        channel = models.Channel.objects.filter(name=name).first()
        if channel is None:
            return ERR_NOSUCHCHANNEL(name)

        if topic is None and not channel.topic:
            return RPL_NOTOPIC(channel.name)

        if topic is None:
            return RPL_TOPIC(channel.name, channel.topic)

        if u"t" in channel.modes and user not in channel.operators:
            return ERR_CHANOPRIVSNEEDED(channel.name)

        channel.topic = topic
        channel.save()

        self.notify(channel.users[:], TOPIC(channel.name, topic, prefix=user.prefix))


class Channel(BasePlugin):

    def init(self, *args, **kwargs):
        super(Channel, self).init(*args, **kwargs)

        self.channellen = 50
        self.topiclen = 300
        self.chantypes = "#&"

        self.chanlimit = {
            u"#": 120,
        }

        self.features = (
            u"PREFIX=(ov)@+",
            u"CHANTYPES={0}".format(self.chantypes),
            u"TOPICLEN={0}".format(self.topiclen),
            u"CHANNELLEN={0}".format(self.channellen),
            u"CHANLIMIT={0}".format(
                u",".join(u"{0}:{1}".format(k, v) for k, v in self.chanlimit.items())
            ),
        )

        Commands(*args, **kwargs).register(self)

    def supports(self):
        return self.features
