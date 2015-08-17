# Module:   plugin
# Date:     16th August 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Plugin Module

This module provides the basic infastructure plugins. All plugins
should subclass BasePlugin to be properly registered as plugins.
"""


from circuits import Component


class BasePlugin(Component):

    channel = "server"

    def init(self, server, config, db):
        self.server = server
        self.config = config
        self.db = db
