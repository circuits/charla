from ..plugin import BasePlugin
from ..commands import BaseCommands


class Commands(BaseCommands):

    def cap(self, sock, source, *args):
        """Not Implemented (yet)"""

        return


class Capability(BasePlugin):

    def init(self, *args, **kwargs):
        super(Capability, self).init(*args, **kwargs)

        Commands(*args, **kwargs).register(self)
