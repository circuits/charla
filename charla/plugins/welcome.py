from itertools import chain


from six import u

from circuits import Event
from circuits.protocols.irc import reply, response
from circuits.protocols.irc.replies import RPL_WELCOME, RPL_YOURHOST
from circuits.protocols.irc.replies import RPL_CREATED, RPL_MYINFO, RPL_ISUPPORT


from .mode import channel_modes, user_modes

from ..plugin import BasePlugin


class supports(Event):
    """supports Event"""


class Welcome(BasePlugin):

    def signon(self, sock, source):
        version = u("{0}-{1}").format(self.server.name, self.server.version)

        umodes = u("").join(user_modes.keys())
        chmodes = u("").join(channel_modes.keys())

        self.fire(reply(sock, RPL_WELCOME(self.server.network)))
        self.fire(reply(sock, RPL_YOURHOST(self.server.host, version)))
        self.fire(reply(sock, RPL_CREATED(self.server.created)))
        self.fire(reply(sock, RPL_MYINFO(self.server.host, version, umodes, chmodes)))

        result = yield self.call(supports())
        self.fire(reply(sock, RPL_ISUPPORT(tuple(chain(*result.value)))))

        self.fire(response.create("lusers", sock, source))
        self.fire(response.create("motd", sock, source))
