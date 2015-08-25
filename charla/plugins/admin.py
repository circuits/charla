from fnmatch import fnmatch


from circuits.protocols.irc import Message


from ..models import User
from ..plugin import BasePlugin
from ..commands import BaseCommands
from ..plugins import load, query, unload
from ..replies import ERR_PASSWDMISMATCH, RPL_YOUREOPER, ERR_NOOPERHOST


class Commands(BaseCommands):

    def oper(self, sock, source, name, password):
        user = User.objects.filter(sock=sock).first()
        if u"o" in user.modes:
            return

        oline = self.parent.oline(user)

        if oline is None:
            return ERR_NOOPERHOST()

        if (name, password) == oline:
            user.modes += u"o"
            user.save()
            return RPL_YOUREOPER()

        return ERR_PASSWDMISMATCH()

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

    olines = {
        u"*!prologic@::ffff:127.0.0.1": (u"prologic", u"test"),
    }

    def init(self, *args, **kwargs):
        super(Admin, self).init(*args, **kwargs)

        Commands(*args, **kwargs).register(self)

    def oline(self, user):
        for k, v in self.olines.items():
            if fnmatch(user.prefix, k):
                return v
