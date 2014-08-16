# Plugin:   mode
# Date:     16th August 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Mode Plugin"""


__version__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from ..plugin import BasePlugin
from ..commands import BaseCommands


class Commands(BaseCommands):

    def mode(self, sock, source, *args):
        """MODE command

        This determines whether the incoming command was a Channel Mode
        command or User Mode command; parses the arguments and fires a
        new event based on the results.
        """


class ModePlugin(BasePlugin):
    """ModeMisc Plugin"""

    def init(self, *args, **kwargs):
        super(ModePlugin, self).init(*args, **kwargs)

        Commands(*args, **kwargs).register(self)
