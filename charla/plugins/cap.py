from ..plugin import BasePlugin
from ..commands import BaseCommands


class Commands(BaseCommands):

    def cap(self, sock, source):
        pass


class Capability(BasePlugin):

    def init(self, *args, **kwargs):
        super(Capability, self).init(*args, **kwargs)

        Commands(*args, **kwargs).register(self)
