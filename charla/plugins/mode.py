from ..plugin import BasePlugin
from ..models import Channel, User
from ..commands import BaseCommands
from ..replies import ERR_NEEDMOREPARAMS, ERR_NOSUCHCHANNEL, ERR_NOSUCHNICK


class Commands(BaseCommands):

    def mode(self, sock, source, *args):
        """MODE command

        This command allows the user to display modes of another user
        or channel and set modes of other users and channels.
        """

        if not args:
            return ERR_NEEDMOREPARAMS("MODE")

        args = iter(args)
        mask = next(args)

        if mask.startswith("#"):
            channel = Channel.objects.filter(name=mask).first()
            if channel is None:
                return ERR_NOSUCHCHANNEL(mask)

            # TODO: Return or Modify Channel Modes
        else:
            user = User.objects.filter(nick=mask).first()
            if user is None:
                return ERR_NOSUCHNICK(mask)

            # TODO: Return or Modify User Modes


class ModePlugin(BasePlugin):
    """Mode Plugin

    This plugin provides commands and support for User and Channel Modes
    """

    __version__ = "0.0.1"
    __author__ = "James Mills, prologic at shortcircuit dot net dot au"

    def init(self, *args, **kwargs):
        super(ModePlugin, self).init(*args, **kwargs)

        Commands(*args, **kwargs).register(self)
