#!/usr/bin/env python


from __future__ import print_function

from socket import socket


from mongoengine import connect


from charla.models import User, Channel


db = connect("test")
db.drop_database("test")

user = User(sock=socket(), nick="foo")
user.save()
channel = Channel(name="#foo")
channel.save()

channel.users.append(user)
channel.save()

user.channels.append(channel)
user.save()

print()
print(Channel.objects(name="#foo").first().users)
