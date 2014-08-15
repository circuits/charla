# Module:   test_basic
# Date:     13th August 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Test Basic Connectivity"""


from circuits import Event

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

    watcher.wait("numeric")
    assert client.events[-1] == Event.create(
        "numeric", 1,
        "Welcome to the {0:s} IRC Network".format(server.network)
    )
