from .. import models
from ..plugin import BasePlugin
from ..commands import BaseCommands
from ..replies import ERR_NONICKNAMEGIVEN
from ..replies import ERR_NOSUCHNICK, ERR_NOSUCHCHANNEL, RPL_WHOREPLY, RPL_ENDOFWHO
from ..replies import RPL_WHOISUSER, RPL_WHOISCHANNELS, RPL_WHOISSERVER, RPL_ENDOFWHOIS


class Commands(BaseCommands):

    def whois(self, sock, source, *args):
        if not args:
            return ERR_NONICKNAMEGIVEN()

        args = iter(args)

        mask = next(args, None)

        user = models.User.objects.filter(nick=mask).first()
        if user is None:
            return ERR_NOSUCHNICK(mask)

        userinfo = user.userinfo

        channels = []
        for channel in user.channels:
            prefix = ""
            if user in channel.operators:
                prefix += "@"
            if user in channel.voiced:
                prefix += "+"
            channels.append(u"{0}{1}".format(prefix, channel.name))

        return [
            RPL_WHOISUSER(user.nick, userinfo.user, userinfo.host, userinfo.name),
            RPL_WHOISCHANNELS(user.nick, channels),
            RPL_WHOISSERVER(user.nick, userinfo.server, "# XXX: TBD"),
            RPL_ENDOFWHOIS(user.nick),
        ]

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
