#!/usr/bin/env python


from __future__ import print_function

from socket import socket


from redisco import connection_setup, get_client


from charla.models import User, Channel


connection_setup()
db = get_client()
db.flushall()

user = User(sock=socket(), nick="foo")
user.save()
channel = Channel(name="#foo")
channel.save()

channel.users.append(user)
channel.save()

user.channels.append(channel)
user.save()

x = Channel.objects.filter(name="#foo").first()

print()
print(Channel.objects.filter(name="#foo").first().users)
