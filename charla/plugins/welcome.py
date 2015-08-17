from circuits.protocols.irc import reply, response
from circuits.protocols.irc.replies import ERR_NOMOTD, RPL_WELCOME, RPL_YOURHOST


from ..plugin import BasePlugin


class WelcomePlugin(BasePlugin):
    """Welcome Plugin"""

    __version__ = "0.0.1"
    __author__ = "James Mills, prologic at shortcircuit dot net dot au"

    def signon(self, sock, source):
        self.fire(reply(sock, RPL_WELCOME(self.server.network)))
        self.fire(reply(sock, RPL_YOURHOST(self.server.host, self.server.version)))
        self.fire(reply(sock, ERR_NOMOTD()))
