from .. import models
from ..plugin import BasePlugin
from ..commands import BaseCommands
from ..replies import ERR_NONICKNAMEGIVEN, ERR_NOMOTD, RPL_LUSEROP
from ..replies import RPL_LUSERCLIENT, RPL_LUSERCHANNELS, RPL_LUSERME
from ..replies import RPL_MOTDSTART, RPL_MOTD, RPL_ENDOFMOTD, RPL_WHOISOPERATOR
from ..replies import ERR_NOSUCHNICK, ERR_NOSUCHCHANNEL, RPL_WHOREPLY, RPL_ENDOFWHO
from ..replies import RPL_WHOISUSER, RPL_WHOISCHANNELS, RPL_WHOISSERVER, RPL_ENDOFWHOIS


class Commands(BaseCommands):

    def lusers(self, sock, source):
        users = models.User.objects.all()
        nusers = len(users)
        nchannels = len(models.Channel.objects.all())
        noperators = len([x for x in users if u"o" in x.modes])
        nservices = 0
        nservers = 1

        return [
            RPL_LUSERCLIENT(nusers, nservices, nservers),
            RPL_LUSERCHANNELS(nchannels),
            RPL_LUSEROP(noperators),
            RPL_LUSERME(nusers, nservers),
        ]

    def motd(self, sock, source):
        if not self.server.motd.exists():
            yield ERR_NOMOTD()
            return

        yield RPL_MOTDSTART(self.server.host)

        with self.server.motd.open("rb") as f:
            yield RPL_MOTD(f.readline().strip())

        yield RPL_ENDOFMOTD()

    def whois(self, sock, source, *args):
        if not args:
            return ERR_NONICKNAMEGIVEN()

        args = iter(args)

        mask = next(args, None)

        user = models.User.objects.filter(nick=mask).first()
        if user is None:
            return ERR_NOSUCHNICK(mask)

        userinfo = user.userinfo
        server = self.parent.server

        channels = []
        for channel in user.channels:
            prefix = ""
            if user in channel.operators:
                prefix += "@"
            if user in channel.voiced:
                prefix += "+"
            channels.append(u"{0}{1}".format(prefix, channel.name))

        # Force :<channels>
        if len(channels) == 1:
            channels.append("")

        replies = []

        replies.append(RPL_WHOISUSER(user.nick, userinfo.user, userinfo.host, userinfo.name))
        replies.append(RPL_WHOISCHANNELS(user.nick, channels))
        replies.append(RPL_WHOISSERVER(user.nick, server.host, server.info))

        if user.oper:
            replies.append(RPL_WHOISOPERATOR(user.nick))

        replies.append(RPL_ENDOFWHOIS(user.nick))

        return replies

    def who(self, sock, source, mask):
        if mask.startswith(u"#"):
            channel = models.Channel.objects.filter(name=mask).first()
            if channel is None:
                return ERR_NOSUCHCHANNEL(mask)

            return [
                RPL_WHOREPLY(user, mask, self.parent.server.host)
                for user in channel.users
            ] + [RPL_ENDOFWHO(mask)]
        else:
            user = models.User.objects.filter(nick=mask).first()
            if user is None:
                return ERR_NOSUCHNICK(mask)

            return (
                RPL_WHOREPLY(user, mask, self.parent.server.host),
                RPL_ENDOFWHO(mask)
            )


class User(BasePlugin):

    def init(self, *args, **kwargs):
        super(User, self).init(*args, **kwargs)

        Commands(*args, **kwargs).register(self)
