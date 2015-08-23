"""Internet Relay Chat Protocol replies

Extended version of circuits.protocols.irc.replies
"""


from circuits.protocols.irc.replies import _M
from circuits.protocols.irc.replies import *  # noqa


def MODE(target, modes, prefix=None):
    return Message("MODE", target, modes, prefix=prefix)


def RPL_CREATED(date):
    return _M("003", "This server was created {0}".format(date))


def RPL_ISUPPORT(features):
    return _M("005", *(features + ("are supported by this server",)))


def RPL_UMODEIS(modes):
    return _M("221", modes)


def ERR_NEEDMOREPARAMS(command):
    return _M("461", command, "Need more parameters")
