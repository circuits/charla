from six import u

from funcy import flatten

from circuits.protocols.irc.replies import RPL_MOTDSTART, RPL_MOTD, RPL_ENDOFMOTD
from circuits.protocols.irc.replies import ERR_NONICKNAMEGIVEN, ERR_NOMOTD, RPL_LUSEROP
from circuits.protocols.irc.replies import RPL_LUSERCLIENT, RPL_LUSERCHANNELS, RPL_LUSERME
from circuits.protocols.irc.replies import RPL_WHOISOPERATOR, RPL_ENDOFWHO, RPL_ENDOFWHOIS
from circuits.protocols.irc.replies import ERR_NOSUCHNICK, ERR_NOSUCHCHANNEL, RPL_WHOREPLY
from circuits.protocols.irc.replies import RPL_WHOISUSER, RPL_WHOISCHANNELS, RPL_WHOISSERVER


from .. import models
from ..plugin import BasePlugin
from ..commands import BaseCommands


class Commands(BaseCommands):

    def lusers(self, sock, source):
        users = models.User.objects.all()
        nusers = len(users)
        nchannels = len(models.Channel.objects.all())
        noperators = len([x for x in users if u("o") in x.modes])
        nservices = 0
        nservers = 1

        return [
            RPL_LUSERCLIENT(nusers, nservices, nservers),
            RPL_LUSERCHANNELS(nchannels),
            RPL_LUSEROP(noperators),
            RPL_LUSERME(nusers, nservers),
        ]

    def motd(self, sock, source):
        if not self.server.motd:
            return ERR_NOMOTD()

        return flatten((
            RPL_MOTDSTART(self.server.host),
            map(RPL_MOTD, self.server.motd),
            RPL_ENDOFMOTD()
        ))

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
            prefix = u("")
            if user in channel.operators:
                prefix += u("@")
            if user in channel.voiced:
                prefix += u("+")
            channels.append(u("{0}{1}").format(prefix, channel.name))

        replies = []

        replies.append(RPL_WHOISUSER(user.nick, userinfo.user, userinfo.host, userinfo.name))
        replies.append(RPL_WHOISCHANNELS(user.nick, channels))
        replies.append(RPL_WHOISSERVER(user.nick, server.host, server.info))

        if user.oper:
            replies.append(RPL_WHOISOPERATOR(user.nick))

        replies.append(RPL_ENDOFWHOIS(user.nick))

        return replies

    def who(self, sock, source, mask):
        if mask and mask[0] in (u("&"), u("#"),):
            channel = models.Channel.objects.filter(name=mask).first()
            if channel is None:
                return ERR_NOSUCHCHANNEL(mask)

            replies = []
            for user in channel.users:
                userinfo = user.userinfo

                status = u("G") if user.away else u("H")
                status += (u("*") if user.oper else u(""))
                status += (u("@") if user in channel.operators else u(""))
                status += (u("+") if user in channel.voiced else u(""))

                replies.append(
                    RPL_WHOREPLY(
                        channel.name, userinfo.user, userinfo.host,
                        self.parent.server.host, user.nick, status,
                        0, userinfo.name or u("")
                    )
                )
            replies.append(RPL_ENDOFWHO(mask))
            return replies
        else:
            user = models.User.objects.filter(nick=mask).first()
            if user is None:
                return ERR_NOSUCHNICK(mask)

            userinfo = user.userinfo

            status = u("G") if user.away else u("H")
            status += (u("*") if user.oper else u(""))

            return (
                RPL_WHOREPLY(
                    mask, userinfo.user, userinfo.host,
                    self.parent.server.host, user.nick, status,
                    0, userinfo.name
                ),
                RPL_ENDOFWHO(mask)
            )


class User(BasePlugin):

    def init(self, *args, **kwargs):
        super(User, self).init(*args, **kwargs)

        Commands(*args, **kwargs).register(self)
