from six import u

from IPy import IP

from circuits import handler, task

from dns import resolver, reversename

from circuits.protocols.irc import reply, Message


from ..events import signon
from ..plugin import BasePlugin
from ..models import User, UserInfo


def lookup(host):
    ip = IP(host)
    addr = reversename.from_address(str(ip))

    try:
        return str(resolver.query(addr, "PTR")[0]).rstrip(".")
    except (resolver.NoAnswer, resolver.NXDOMAIN):
        if ip.iptype() == "IPV4MAP":
            return str(ip.v46map())
        return str(ip)


def check_host(sock):
    return lookup(sock.getpeername()[0])


class CheckHost(BasePlugin):

    def init(self, *args, **kwargs):
        super(CheckHost, self).init(*args, **kwargs)

        self.pending = {}

    def task_complete(self, e, value):
        _, sock = e.args
        del self.pending[sock]

        self.fire(reply(sock, Message(u("NOTICE"), u("*"), u("*** Found your hostname"))))

        user = User.objects.filter(sock=sock).first()
        if user is None:
            return

        if user.userinfo is None:
            userinfo = UserInfo()
            userinfo.save()

            user.userinfo = userinfo
            user.save()

        user.userinfo.host = value
        user.userinfo.save()

        if user.registered:
            self.fire(signon(user.sock, user.source))
        else:
            self.logger.warn(u("User {0} is not registered!").format(user.nick))

    def connect(self, sock, *args):
        host, port = args[:2]
        self.pending[sock] = True
        self.fire(reply(sock, Message(u("NOTICE"), u("*"), u("*** Looking up your hostname..."))))

        e = task(check_host, sock)
        e.complete = True
        e.complete_channels = ("server",)

        self.fire(e, "threadpool")

    @handler("signon", priority=1.0)
    def signon(self, event, sock, source):
        if self.pending.get(sock, False):
            event.stop()
