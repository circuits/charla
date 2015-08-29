from six import u

from circuits.protocols.irc import Message


from ..plugin import BasePlugin
from ..commands import BaseCommands


class Commands(BaseCommands):

    def ping(self, sock, source, *args):
        return Message(u("PONG"), u(" ").join(args))


class Ping(BasePlugin):

    def init(self, *args, **kwargs):
        super(Ping, self).init(*args, **kwargs)

        Commands(*args, **kwargs).register(self)
