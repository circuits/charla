from circuits.protocols.irc import Message


from ..plugin import BasePlugin
from ..commands import BaseCommands


class Commands(BaseCommands):

    def hello(self, sock, source, server):
        return Message("PONG", server)


class MiscPlugin(BasePlugin):
    """Misc Plugin"""

    __version__ = "0.0.1"
    __author__ = "James Mills, prologic at shortcircuit dot net dot au"

    def init(self, *args, **kwargs):
        super(MiscPlugin, self).init(*args, **kwargs)

        Commands(*args, **kwargs).register(self)
