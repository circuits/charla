# Module:   client
# Date:     13th August 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Test Client"""


from circuits import handler, Component

from circuits.net.sockets import TCPClient, connect

from circuits.protocols.irc import IRC


class Client(Component):

    channel = "client"

    def init(self, host, port="6667", channel=channel):
        self.host = host
        self.port = int(port)

        self.connected = False
        self.events = []

        self.transport = TCPClient(channel=self.channel).register(self)
        self.protocol = IRC(channel=self.channel).register(self)

    def ready(self, component):
        self.fire(connect(self.host, self.port))

    def connected(self, host, port):
        self.connected = True

    def disconnected(self):
        self.connected = False

    @handler()
    def _on_event(self, event, *args, **kwargs):
        self.events.append(event)
