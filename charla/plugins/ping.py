from circuits.protocols.irc.replies import PONG


from ..plugin import BasePlugin
from ..commands import BaseCommands


class Commands(BaseCommands):

    def ping(self, sock, source, *args):
        return PONG(*args)


class Ping(BasePlugin):

    def init(self, *args, **kwargs):
        super(Ping, self).init(*args, **kwargs)

        Commands(*args, **kwargs).register(self)
