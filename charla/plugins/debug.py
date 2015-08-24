from ..models import User
from ..plugin import BasePlugin


class Debug(BasePlugin):

    def init(self, *args, **kwargs):
        super(Debug, self).init(*args, **kwargs)

    def connect(self, sock, *args):
        host, port = args[:2]
        self.logger.info(u"C: [{0:s}:{1:d}]".format(host, port))

    def disconnect(self, sock):
        user = User.objects.filter(sock=sock).first()
        if user is None:
            return

        self.logger.info(u"D: [{0:s}:{1:d}]".format(user.host, user.port))

    def read(self, sock, data):
        user = User.objects.filter(sock=sock).first()

        host, port = user.host, user.port

        self.logger.info(u"I: [{0:s}:{1:d}] {2:s}".format(host, port, repr(data)))

    def write(self, sock, data):
        user = User.objects.filter(sock=sock).first()
        if user is None:
            return

        host, port = user.host, user.port

        self.logger.info(u"O: [{0:s}:{1:d}] {2:s}".format(host, port, repr(data)))
