from itertools import chain


from circuits import Event
from circuits.protocols.irc import reply


from ..plugin import BasePlugin
from ..replies import ERR_NOMOTD, RPL_WELCOME, RPL_YOURHOST, RPL_CREATED, RPL_ISUPPORT


class supports(Event):
    """supports Event"""


class Welcome(BasePlugin):

    def signon(self, sock, source):
        version = u"{0} {1}".format(self.server.name, self.server.version)

        self.fire(reply(sock, RPL_WELCOME(self.server.network)))
        self.fire(reply(sock, RPL_YOURHOST(self.server.host, version)))
        self.fire(reply(sock, RPL_CREATED(self.server.created)))

        # XXX: 004?

        result = yield self.call(supports())
        self.fire(reply(sock, RPL_ISUPPORT(tuple(chain(*result.value)))))

        if not self.server.motd.exists():
            self.fire(reply(sock, ERR_NOMOTD()))
