"""Plugin Module

This module provides the basic infastructure plugins. All plugins
should subclass BasePlugin to be properly registered as plugins.
"""


from logging import getLogger


from circuits import Component


class BasePlugin(Component):

    channel = "server"

    def init(self, server, config, db):
        self.server = server
        self.config = config
        self.db = db

        self.logger = getLogger("plugins.{0}".format(self.__class__.__name__))
