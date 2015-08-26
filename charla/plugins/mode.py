from itertools import imap
from operator import attrgetter


from six import u
from funcy import take


from ..plugin import BasePlugin
from ..models import Channel, User
from ..commands import BaseCommands
from ..replies import MODE, RPL_UMODEIS, RPL_CHANNELMODEIS
from ..replies import ERR_NEEDMOREPARAMS, ERR_NOSUCHCHANNEL, ERR_NOSUCHNICK
from ..replies import ERR_CHANOPRIVSNEEDED, ERR_UNKNOWNMODE, ERR_USERNOTINCHANNEL


def process_channel_mode(user, channel, mode, *args, **kwargs):
    op = kwargs.get("op", None)

    if op is not None and not user.oper and user not in channel.operators:
        yield False, ERR_CHANOPRIVSNEEDED(channel.name)
        return

    if op == u("+"):
        if mode in channel.modes:
            yield False, None
            return
        channel.modes += mode
    else:
        if mode not in channel.modes:
            yield False, None
            return
        channel.modes = channel.modes.replace(mode, u(""))

    channel.save()

    yield True, MODE(channel.name, u("{0}{1}").format(op, mode), prefix=user.prefix)


def process_channel_mode_ov(user, channel, mode, *args, **kwargs):
    op = kwargs.get("op", None)

    if op is not None and not user.oper and user not in channel.operators:
        yield False, ERR_CHANOPRIVSNEEDED(channel.name)
        return

    nick = args[0]
    if nick not in imap(attrgetter("nick"), channel.users):
        yield False, ERR_USERNOTINCHANNEL(nick, channel.name)
        return

    nick = User.objects.filter(nick=nick).first()

    if mode == u("o"):
        collection = channel.operators
    elif mode == u("v"):
        collection = channel.voiced

    if op == u("+"):
        collection.append(nick)
        channel.save()

        yield True, MODE(channel.name, u("{0}{1}").format(op, mode), [nick.nick], prefix=user.prefix)
    elif op == u("-"):
        collection.remove(nick)
        channel.save()

        yield True, MODE(channel.name, u("{0}{1}").format(op, mode), [nick.nick], prefix=user.prefix)


channel_modes = {
    u("n"): (0, process_channel_mode),
    u("t"): (0, process_channel_mode),
    u("o"): (1, process_channel_mode_ov),
    u("v"): (1, process_channel_mode_ov),
}


def process_channel_modes(user, channel, modes):
    op = None
    modes = iter(modes)
    while True:
        try:
            mode = next(modes)

            if mode and mode[0] == u("+"):
                op = u("+")
                mode = mode[1:]
            elif mode and mode[0] == u("-"):
                op = u("-")
                mode = mode[1:]

            if mode not in channel_modes:
                yield False, ERR_UNKNOWNMODE(mode)
            else:
                nargs, f = channel_modes[mode]
                for notify, message in f(user, channel, mode, *take(nargs, modes), op=op):
                    yield notify, message
        except StopIteration:
            break


def process_user_mode(user, mode, op=None):
    if op == u("+"):
        if mode in user.modes:
            return
        user.modes += mode
    else:
        if mode not in user.modes:
            return
        user.modes = user.modes.replace(mode, u(""))

    user.save()

    return MODE(user.nick, u("{0}{1})").format(op, mode), prefix=user.nick)


user_modes = {
    u("i"): (0, process_user_mode),
}


def process_user_modes(user, modes):
    op = None
    modes = iter(modes)
    while True:
        try:
            mode = next(modes)

            if mode and mode[0] == u("+"):
                op = u("+")
                mode = mode[1:]
            elif mode and mode[0] == u("-"):
                op = u("-")
                mode = mode[1:]

            if mode not in user_modes:
                yield ERR_UNKNOWNMODE(mode)
            else:
                nargs, f = user_modes[mode]
                yield f(user, mode, op=op)
        except StopIteration:
            break


class Commands(BaseCommands):

    def _process_channel_modes(self, user, channel, modes):
        for notify, message in process_channel_modes(user, channel, modes):
            if notify:
                self.notify(channel.users[:], message)
            elif message is not None:
                yield message

    def mode(self, sock, source, *args):
        """MODE command

        This command allows the user to display modes of another user
        or channel and set modes of other users and channels.
        """

        if not args:
            return ERR_NEEDMOREPARAMS(u"MODE")

        args = iter(args)
        mask = next(args)

        if mask.startswith(u("#")):
            channel = Channel.objects.filter(name=mask).first()
            if channel is None:
                return ERR_NOSUCHCHANNEL(mask)

            user = User.objects.filter(sock=sock).first()

            mode = next(args, None)
            if mode is None:
                return RPL_CHANNELMODEIS(channel.name, u("+{0}").format(channel.modes))

            return self._process_channel_modes(user, channel, [mode] + list(args))
        else:
            user = User.objects.filter(nick=mask).first()
            if user is None:
                return ERR_NOSUCHNICK(mask)

            mode = next(args, None)
            if mode is None:
                return RPL_UMODEIS(u("+{0}").format(user.modes))

            return process_user_modes(user, [mode] + list(args))


class Mode(BasePlugin):

    def init(self, *args, **kwargs):
        super(Mode, self).init(*args, **kwargs)

        self.chanmodes = u",,,nt"

        self.features = (
            u"CHANMODES={0}".format(self.chanmodes),
        )

        Commands(*args, **kwargs).register(self)

    def supports(self):
        return self.features
