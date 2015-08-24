from socket import getaddrinfo, gethostbyaddr, AF_INET6


from circuits import handler, task
from circuits.protocols.irc import reply, Message


from ..events import signon
from ..plugin import BasePlugin
from ..models import User, UserInfo


def check_host(sock):
    host = sock.getpeername()[0]
    if ":" in host:
        return getaddrinfo(host, None, AF_INET6)[0][-1][0]
    return gethostbyaddr(host)[0]


class CheckHost(BasePlugin):

    def init(self, *args, **kwargs):
        super(CheckHost, self).init(*args, **kwargs)

        self.pending = {}

    def task_complete(self, e, value):
        _, sock = e.args
        del self.pending[sock]

        self.fire(reply(sock, Message(u"NOTICE", u"*", u"*** Found your hostname")))

        user = User.objects.filter(sock=sock).first()

        if user.userinfo is None:
            userinfo = UserInfo()
            userinfo.save()

            user.userinfo = userinfo
            user.save()

        user.userinfo.host = value
        user.userinfo.save()

        if user.registered:
            return signon(sock, user.source)

    def connect(self, sock, *args):
        host, port = args[:2]
        self.pending[sock] = True
        self.fire(reply(sock, Message(u"NOTICE", u"*", u"*** Looking up your hostname...")))

        e = task(check_host, sock)
        e.complete = True
        e.complete_channels = ("server",)

        self.fire(e, "threadpool")

    @handler("signon", priority=1.0)
    def signon(self, event, sock, source):
        if self.pending.get(sock, False):
            event.stop()
