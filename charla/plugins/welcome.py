from circuits.protocols.irc import reply


from ..plugin import BasePlugin
from ..replies import ERR_NOMOTD, RPL_WELCOME, RPL_YOURHOST, RPL_CREATED, RPL_ISUPPORT


class Welcome(BasePlugin):
    """Welcome Plugin"""

    __version__ = "0.0.1"
    __author__ = "James Mills, prologic at shortcircuit dot net dot au"

    def signon(self, sock, source):
        version = "{0} {1}".format(self.server.name, self.server.version)

        self.fire(reply(sock, RPL_WELCOME(self.server.network)))
        self.fire(reply(sock, RPL_YOURHOST(self.server.host, version)))
        self.fire(reply(sock, RPL_CREATED(self.server.created)))
        # XXX: 004?
        self.fire(reply(sock, RPL_ISUPPORT(self.server.features)))

        self.fire(reply(sock, ERR_NOMOTD()))
