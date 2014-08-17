# Plugin:   misc
# Date:     16th August 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Misc Plugin"""


__version__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from circuits.protocols.irc import Message


from ..plugin import BasePlugin
from ..commands import BaseCommands


class Commands(BaseCommands):

    def ping(self, sock, source, server):
        return Message("PONG", server)


class MiscPlugin(BasePlugin):
    """Misc Plugin"""

    def init(self, *args, **kwargs):
        super(MiscPlugin, self).init(*args, **kwargs)

        Commands(*args, **kwargs).register(self)
