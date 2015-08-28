import os
import sys
from fnmatch import fnmatch


from circuits.net.events import close
from circuits.protocols.irc import reply, response
from circuits.protocols.irc.replies import Message, ERR_NOSUCHNICK, ERROR
from circuits.protocols.irc.replies import ERR_PASSWDMISMATCH, RPL_YOUREOPER, ERR_NOOPERHOST, ERR_NOPRIVILEGES


from ..models import User
from ..plugin import BasePlugin
from ..commands import BaseCommands
from ..plugins import load, query, unload


class Commands(BaseCommands):

    def oper(self, sock, source, name, password):
        user = User.objects.filter(sock=sock).first()
        if user.oper:
            return

        oline = self.parent.oline(user)

        if oline is None:
            return ERR_NOOPERHOST()

        if (name, password) == oline:
            user.modes += u"o"
            user.save()
            return RPL_YOUREOPER()

        return ERR_PASSWDMISMATCH()

    def load(self, sock, source, name):
        user = User.objects.filter(sock=sock).first()
        if not user.oper:
            yield ERR_NOPRIVILEGES()
            return

        name = str(name)  # We store plugin names as str (not unicode)

        result = yield self.call(load(name), "plugins")
        yield Message(u"NOTICE", u"*", result.value)

    def reload(self, sock, source, name):
        user = User.objects.filter(sock=sock).first()
        if not user.oper:
            yield ERR_NOPRIVILEGES()
            return

        name = str(name)  # We store plugin names as str (not unicode)
        result = yield self.call(query(name), "plugins")

        if result.value is None:
            yield Message(u"NOTICE", u"*", u"No such plugin: {0}".format(name))
            return

        result = yield self.call(unload(name), "plugins")
        yield Message(u"NOTICE", u"*", result.value)

        result = yield self.call(load(name), "plugins")
        yield Message(u"NOTICE", u"*", result.value)

    def unload(self, sock, source, name):
        user = User.objects.filter(sock=sock).first()
        if not user.oper:
            yield ERR_NOPRIVILEGES()
            return

        name = str(name)  # We store plugin names as str (not unicode)
        result = yield self.call(query(name), "plugins")

        if result.value is None:
            yield Message(u"NOTICE", u"*", u"No such plugin: {0}".format(name))
            return

        result = yield self.call(unload(name), "plugins")
        yield Message(u"NOTICE", u"*", result.value)

    def die(self, sock, source):
        user = User.objects.filter(sock=sock).first()
        if not user.oper:
            return ERR_NOPRIVILEGES()

        raise SystemExit(0)

    def restart(self, sock, source):
        user = User.objects.filter(sock=sock).first()
        if not user.oper:
            yield ERR_NOPRIVILEGES()
            return

        yield self.call(close(), "server")

        args = sys.argv[:]
        self.parent.logger.info(u"Restarting... Args: {0}".format(args))

        args.insert(0, sys.executable)
        if sys.platform == 'win32':
            args = ['"%s"' % arg for arg in args]

        os.execv(sys.executable, args)

    def kill(self, sock, source, target, reason=None):
        user = User.objects.filter(sock=sock).first()
        if not user.oper:
            return ERR_NOPRIVILEGES()

        nick = User.objects.filter(nick=target).first()
        if nick is None:
            return ERR_NOSUCHNICK(target)

        reason = u"Killed: {0}".format(reason) if reason else u"Killed"

        self.fire(response.create("quit", nick.sock, nick.source, reason, disconnect=False))
        self.fire(reply(nick.sock, ERROR(reason)))
        self.fire(close(nick.sock))


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
