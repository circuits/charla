# Module:   commands
# Date:     16th August 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Commands Module

This module provides a base component for all commands handling.
"""


from circuits import handler, Component

from circuits.net.events import close


from .events import broadcast


class BaseCommands(Component):

    channel = "commands"

    def init(self, server, config, db):
        self.server = server
        self.config = config
        self.db = db

    @handler(False)
    def disconnect(self, user):
        self.fire(close(user.sock), self.server.channel)

    @handler(False)
    def notify(self, users, message, *exclude):
        self.fire(broadcast(users, message, *exclude), self.server.channel)
