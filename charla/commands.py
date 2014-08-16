# Module:   commands
# Date:     16th August 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Commands Module

This module provides a base component for all commands handling.
"""


from circuits import Component


class BaseCommands(Component):

    channel = "commands"

    def init(self, server, config, data):
        self.server = server
        self.config = config
        self.data = data
