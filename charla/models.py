# Module:   models
# Date:     16th August 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Data Models"""


from datetime import datetime
from socket import error as SocketError


from bidict import bidict

from circuits.protocols.irc import joinprefix

from mongoengine import EmbeddedDocument, Document
from mongoengine.fields import (
    BaseField, BooleanField, DateTimeField, EmbeddedDocumentField,
    IntField, ListField, ReferenceField, StringField
)


class SocketField(BaseField):

    cache = bidict()

    def __init__(self, **kwargs):
        super(SocketField, self).__init__(**kwargs)

    def to_mongo(self, value):
        print("SocketField.to_mongo:")
        fd = value.fileno()
        self.cache[fd] = value
        return fd

    def to_python(self, value):
        print("SocketField.to_python:")
        return self.cache[value] if value in self.cache else value

    def prepare_query_value(self, op, v):
        print("SocketField.prepare_query_value:")
        try:
            return v.fileno()
        except SocketError:
            return None


class Channel(Document):

    name = StringField(primary_key=True, required=True, unique=True)

    users = ListField(ReferenceField("User"))


class UserInfo(EmbeddedDocument):

    user = StringField()
    host = StringField()
    name = StringField()
    server = StringField()


class User(Document):

    sock = SocketField(required=True, unique=True)

    host = StringField()
    port = IntField()

    nick = StringField(default=None)
    away = StringField(default=None)

    channels = ListField(ReferenceField("Channel"))

    registered = BooleanField(default=False)

    userinfo = EmbeddedDocumentField("UserInfo")

    signon = DateTimeField(default=datetime.now)

    def delete(self, *args, **kwargs):
        print("User.delete")
        del SocketField.cache[:self.sock]
        super(User, self).delete(*args, **kwargs)

    @property
    def prefix(self):
        userinfo = self.userinfo
        if userinfo is None:
            return
        return joinprefix(self.nick, userinfo.user, userinfo.host)
