from ..models import User
from ..plugin import BasePlugin


class DebugPlugin(BasePlugin):
    """DebugHello Plugin"""

    __version__ = "0.0.1"
    __author__ = "James Mills, prologic at shortcircuit dot net dot au"

    def init(self, *args, **kwargs):
        super(DebugPlugin, self).init(*args, **kwargs)

    def connect(self, sock, *args):
        host, port = args[:2]
        self.logger.info("C: [{0:s}:{1:d}]".format(host, port))

    def disconnect(self, sock):
        user = User.objects.filter(sock=sock).first()
        if user is None:
            return

        self.logger.info("D: [{0:s}:{1:d}]".format(user.host, user.port))

    def read(self, sock, data):
        user = User.objects.filter(sock=sock).first()

        host, port = user.host, user.port

        self.logger.info(
            "I: [{0:s}:{1:d}] {2:s}".format(host, port, repr(data))
        )

    def write(self, sock, data):
        user = User.objects.filter(sock=sock).first()
        if user is None:
            return

        host, port = user.host, user.port

        self.logger.info(
            "O: [{0:s}:{1:d}] {2:s}".format(host, port, repr(data))
        )
