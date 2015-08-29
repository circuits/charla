from six import u

from circuits.protocols.irc import response


from ..plugin import BasePlugin


class AutoJoin(BasePlugin):

    def signon(self, sock, source):
        # Force users to join #circuits
        self.fire(response.create("join", sock, source, u("#circuits")))
