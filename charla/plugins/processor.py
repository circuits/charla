from inspect import getargspec
from types import GeneratorType


from six import u

from cidict import cidict

from circuits import handler, Event

from circuits.net.events import write

from circuits.protocols.irc import reply, response, Message

from circuits.protocols.irc.replies import ERR_UNKNOWNCOMMAND
from circuits.protocols.irc.replies import ERR_NEEDMOREPARAMS, ERR_NOTREGISTERED


from ..models import User
from ..plugin import BasePlugin


class Processor(BasePlugin):

    def init(self, *args, **kwargs):
        super(Processor, self).init(*args, **kwargs)

        # command -> plugin
        self.command = cidict()

        # plugin name -> commands
        self.commands = cidict()

        # plugin name -> plugin
        self.plugins = cidict()

    @handler("registered", channel="*")
    def _on_registered(self, component, manager):
        if component.channel == "commands":
            for event in component.events():
                if event not in self.command:
                    self.command[event] = component

            if component.parent.name in self.commands:
                events = self.commands[component.parent.name]
                events = events.union(component.events())
                self.commands[component.parent.name] = events
            else:
                self.commands[component.parent.name] = set(component.events())

        if isinstance(component, BasePlugin):
            if component.name not in self.plugins:
                self.plugins[component.name] = component

    @handler("unregistered", channel="*")
    def _on_unregistered(self, component, manager):
        if component.channel == "commands":
            for event in component.events():
                if event in self.command:
                    del self.command[event]

        if isinstance(component, BasePlugin):
            if component.name in self.commands:
                del self.commands[component.name]
            if component.name in self.plugins:
                del self.plugins[component.name]

    def quit_complete(self, e, value):
        sock = e.args[0]
        user = User.objects.filter(sock=sock).first()
        if user is None:
            return

        user.delete()

    def broadcast(self, users, message, *exclude):
        for user in users:
            if user in exclude:
                continue

            self.fire(reply(user.sock, message))

    def reply(self, sock, message):
        user = User.objects.filter(sock=sock).first()

        if message.add_nick:
            message.args.insert(0, user.nick or u(""))

        if message.prefix is None:
            message.prefix = self.server.host

        self.fire(write(sock, bytes(message)))

    @handler()  # noqa
    def _on_event(self, event, *args, **kwargs):
        name = event.name
        if name in ("generate_events",) or name.endswith("_done"):
            return

        if name.endswith("_complete") and isinstance(args[0], response):
            e, value = args
            if value is None:
                return

            values = (
                (value,) if not isinstance(value, (GeneratorType, tuple, list,))
                else value
            )

            sock, source = e.args[:2]
            args = e.args[2:]

            for value in values:
                if isinstance(value, Message):
                    self.fire(reply(sock, value))
                elif isinstance(value, Event):
                    self.fire(value)
                else:
                    self.logger.warn(
                        u("Handler for {0:s} returned unknown type {1} ({2})").format(
                            name,
                            value.__class__.__name__,
                            repr(value)
                        )
                    )
        elif isinstance(event, response):
            sock = args[0]
            user = User.objects.filter(sock=sock).first()

            if user and not user.registered and event.name not in ("nick", "cap", "pass", "user",):
                return self.fire(reply(sock, ERR_NOTREGISTERED()))

            if event.name not in self.command:
                event.stop()
                return self.fire(reply(sock, ERR_UNKNOWNCOMMAND(event.name)))

            component = self.command[event.name]
            handlers = (x for x in type(component).handlers() if event.name in x.names)
            handler = next(handlers, None)
            assert handler is not None

            argspec = getargspec(handler)
            args = list(argspec.args)
            for skip in ("self", "event",):
                if args and args[0] == skip:
                    del args[0]

            if len(args) < (len(args) - len(argspec.defaults or ())):
                event.stop()
                return self.fire(reply(sock, ERR_NEEDMOREPARAMS(event.name)))

            event.complete = True
            event.complete_channels = ("server",)
            self.fire(event, "commands")
