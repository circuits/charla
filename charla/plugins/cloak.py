from os import urandom
from hashlib import sha256


from ..models import User
from ..plugin import BasePlugin


class Cloak(BasePlugin):

    def signon(self, sock, source):
        user = User.objects.filter(sock=sock).first()
        user.userinfo.host = sha256("{0}{1}".format(urandom(10), user.host)).hexdigest()[-7:]
        user.userinfo.save()
