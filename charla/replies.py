"""Internet Relay Chat Protocol replies

Extended version of circuits.protocols.irc.replies
"""


from circuits.protocols.irc.replies import _M
from circuits.protocols.irc.replies import *  # noqa


def MODE(target, modes, params=None, prefix=None):
    if params is None:
        return Message("MODE", target, modes, prefix=prefix)
    return Message("MODE", target, modes, " ".join(params), prefix=prefix)


def JOIN(name, prefix=None):
    return Message("JOIN", name, prefix=prefix)


def RPL_CREATED(date):
    return _M("003", "This server was created {0}".format(date))


def RPL_ISUPPORT(features):
    return _M("005", *(features + ("are supported by this server",)))


def RPL_UMODEIS(modes):
    return _M("221", modes)


def RPL_CHANNELMODEIS(channel, mode, params=None):
    if params is None:
        return _M("324", channel, mode)
    return _M("324", channel, mode, params)


def RPL_VERSION(name, version, hostname, url):
    return _M("351", name, version, hostname, url)


def ERR_USERNOTINCHANNEL(nick, channel):
    return _M("441", nick, channel, "They aren't on that channel")


def ERR_NEEDMOREPARAMS(command):
    return _M("461", command, "Need more parameters")


def ERR_CHANOPRIVSNEEDED(channel):
    return _M("482", channel, "You're not channel operator")


def ERR_UNKNOWNMODE(mode, channel=None):
    if channel is None:
        return _M("472", mode, "is unknown mode char to me")
    return _M("472", mode, "is unknown mode char to me for channel {1}".format(channel))
