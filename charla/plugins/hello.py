from six import u

from circuits.protocols.irc import Message


from ..plugin import BasePlugin
from ..commands import BaseCommands


class Commands(BaseCommands):

    def hello(self, sock, source):
        return Message(u("NOTICE"), u("*"), u("Hello!"))


class Hello(BasePlugin):

    def init(self, *args, **kwargs):
        super(Hello, self).init(*args, **kwargs)

        Commands(*args, **kwargs).register(self)
