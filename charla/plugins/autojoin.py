from circuits.protocols.irc import response


from ..plugin import BasePlugin


class AutoJoin(BasePlugin):
    """AutoJoin Plugin"""

    __version__ = "0.0.1"
    __author__ = "James Mills, prologic at shortcircuit dot net dot au"

    def signon(self, sock, source):
        # Force users to join #circuits
        # self.fire(request.create("JOIN", sock, source, "#circuits"))
        self.fire(response.create("join", sock, source, "#circuits"))
