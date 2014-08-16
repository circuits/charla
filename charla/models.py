# Module:   models
# Date:     16th August 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Data Models"""


from datetime import datetime


from circuits.protocols.irc import joinprefix


class Channel(object):

    def __init__(self, name):
        self.name = name

        self.users = []


class User(object):

    def __init__(self, sock, host="", port=0):
        self.sock = sock
        self.host = host
        self.port = port

        self.nick = None
        self.away = None
        self.channels = []
        self.registered = False
        self.userinfo = UserInfo()
        self.signon = datetime.now()

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
