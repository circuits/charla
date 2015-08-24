from ..plugin import BasePlugin
from ..replies import RPL_VERSION
from ..commands import BaseCommands


class Commands(BaseCommands):

    def version(self, sock, source):
        return RPL_VERSION(self.server.name, self.server.version, self.server.host, self.server.url)


class Version(BasePlugin):

    def init(self, *args, **kwargs):
        super(Version, self).init(*args, **kwargs)

        Commands(*args, **kwargs).register(self)
