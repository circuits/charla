from circuits.protocols.irc import Message


from ..plugin import BasePlugin
from ..commands import BaseCommands
from ..plugins import load, query, unload


class Commands(BaseCommands):

    def reload(self, sock, source, name):
        name = str(name)  # We store plugin names as str (not unicode)
        result = yield self.call(query(name), "plugins")

        if result.value is None:
            yield Message(u"NOTICE", u"*", u"No such plugin: {0}".format(name))
            return

        result = yield self.call(unload(name), "plugins")
        yield Message(u"NOTICE", u"*", result.value)

        result = yield self.call(load(name), "plugins")
        yield Message(u"NOTICE", u"*", result.value)


class Admin(BasePlugin):

    def init(self, *args, **kwargs):
        super(Admin, self).init(*args, **kwargs)

        Commands(*args, **kwargs).register(self)
