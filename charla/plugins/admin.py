from circuits.protocols.irc import Message


from ..plugin import BasePlugin
from ..commands import BaseCommands
from ..plugins import load, query, unload


class Commands(BaseCommands):

    def reload(self, sock, source, name):
        name = str(name)  # We store plugin names as str (not unicode)
        result = yield self.call(query(name), "plugins")

        if result.value is None:
            yield Message("NOTICE", "*", "No such plugin: {0}".format(name))
            return

        result = yield self.call(unload(name), "plugins")
        yield Message("NOTICE", "*", result.value)

        result = yield self.call(load(name), "plugins")
        yield Message("NOTICE", "*", result.value)


class Admin(BasePlugin):
    """Admin Plugin"""

    __version__ = "0.0.1"
    __author__ = "James Mills, prologic at shortcircuit dot net dot au"

    def init(self, *args, **kwargs):
        super(Admin, self).init(*args, **kwargs)

        Commands(*args, **kwargs).register(self)
