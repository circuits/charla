# Module:   models
# Date:     13th August 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Data Models"""


from circuits.protocols.irc import joinprefix


class Channel(object):

    def __init__(self, name):
        self.name = name

        self.users = []


class User(object):

    def __init__(self, sock, host, port):
        self.sock = sock
        self.host = host
        self.port = port

        self.nick = None
        self.away = False
        self.channels = []
        self.signon = None
        self.registered = False
        self.userinfo = UserInfo()

    @property
    def prefix(self):
        userinfo = self.userinfo
        return joinprefix(self.nick, userinfo.user, userinfo.host)


class UserInfo(object):

    def __init__(self, user=None, host=None, server=None, name=None):
        self.user = user
        self.host = host
        self.server = server
        self.name = name

    def __nonzero__(self):
        return all(x is not None for x in (self.user, self.host, self.name))
