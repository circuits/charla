# Module:   test_core
# Date:     16th August 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Test Core"""


from __future__ import print_function


from circuits.net.events import close

from circuits.protocols.irc import NICK, USER


def test_connection(client):
    assert client.connected


def test_disconnection(client, watcher):
    client.fire(close())
    watcher.wait("disconnected")
    assert not client.connected


def test_registration(server, client, watcher):
    client.fire(NICK("test"))
    client.fire(USER("test", "localhost", server.host, "Test Client"))

    assert watcher.wait("numeric")

    assert client.expect(
        "numeric", [
            (u'localhost', None, None), 1, u"test",
            u"Welcome to the {0:s} IRC Network".format(server.network)
        ]
    )
