from time import time


from six import u

from circuits import Event, Timer

from circuits.net.events import close, write

from circuits.protocols.irc import reply, response

from circuits.protocols.irc.replies import ERROR, PING, PONG


from ..models import User
from ..plugin import BasePlugin
from ..commands import BaseCommands


class poll(Event):
    """poll Event"""


class Commands(BaseCommands):

    def ping(self, sock, source, text):
        return PONG(self.server.host, text)

    def pong(self, sock, source, server):
        user = User.objects.filter(sock=sock).first()
        user.lastpong = int(time())
        user.save()


class Ping(BasePlugin):

    def init(self, *args, **kwargs):
        super(Ping, self).init(*args, **kwargs)

        self.timeout = 10

        Commands(*args, **kwargs).register(self)

        Timer(30, poll(), self.channel, persist=True).register(self)

    def poll(self):
        now = int(time())
        reason = u("Ping timeout: {0} seconds")

        for user in User.objects.all():
            if user.lastping and not user.lastpong and ((now - user.lastping) > self.timeout):
                delta = now - user.lastping
                self.fire(response.create("quit", user.sock, user.source, reason.format(delta)))
                self.fire(reply(user.sock, ERROR(user.host, reason.format(delta))), "server")
                Timer(1, close(user.sock), "server").register(self)
            else:
                self.fire(write(user.sock, bytes(PING(self.server.host))))
                user.lastping = int(time())
                user.lastpong = None
                user.save()
