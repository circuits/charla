from ..plugin import BasePlugin
from ..replies import RPL_VERSION
from ..commands import BaseCommands


class Commands(BaseCommands):

    def version(self, sock, source):
        return RPL_VERSION(self.server.name, self.server.version, self.server.host, self.server.url)


class VersionPlugin(BasePlugin):
    """VersionHello Plugin"""

    __version__ = "0.0.1"
    __author__ = "James Mills, prologic at shortcircuit dot net dot au"

    def init(self, *args, **kwargs):
        super(VersionPlugin, self).init(*args, **kwargs)

        Commands(*args, **kwargs).register(self)
