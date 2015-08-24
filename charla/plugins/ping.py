from circuits.protocols.irc import Message


from ..plugin import BasePlugin
from ..commands import BaseCommands


class Commands(BaseCommands):

    def ping(self, sock, source, server):
        return Message(u"PONG", server)


class Ping(BasePlugin):

    def init(self, *args, **kwargs):
        super(Ping, self).init(*args, **kwargs)

        Commands(*args, **kwargs).register(self)
