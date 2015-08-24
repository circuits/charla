from .. import models
from ..plugin import BasePlugin
from ..commands import BaseCommands
from ..replies import ERR_NOSUCHNICK, ERR_NOSUCHCHANNEL, RPL_WHOREPLY, RPL_ENDOFWHO


class Commands(BaseCommands):

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
