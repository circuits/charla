from __future__ import print_function


import sys
from logging import getLogger
from traceback import format_exc
from inspect import getmembers, isclass


from pymills.utils import safe__import__


from circuits.tools import kill
from circuits import Event, Component

from cidict import cidict


from ..plugin import BasePlugin


DEFAULTS = (
    "admin", "autojoin", "cap", "core", "channel", "checkhost", "debug",
    "message", "mode", "user", "ping", "processor", "welcome", "version",
)


class load(Event):
    """load Event"""


class query(Event):
    """query Event"""


class unload(Event):
    """unload Event"""


class Plugins(Component):

    channel = "plugins"

    def init(self, init_args=None, init_kwargs=None):
        self.init_args = init_args or tuple()
        self.init_kwargs = init_kwargs or dict()

        self.logger = getLogger(__name__)

        self.plugins = cidict()

    def query(self, name=None):
        if name is None:
            return self.plugins
        else:
            return self.plugins.get(name, None)

    def load(self, name, package=__package__):
        if name in self.plugins:
            msg = u"Not loading already loaded plugin: {0:s}".format(name)
            self.logger.warn(msg)
            return msg

        try:
            fqplugin = "{0:s}.{1:s}".format(package, name)
            if fqplugin in sys.modules:
                reload(sys.modules[fqplugin])

            m = safe__import__(name, globals(), locals(), package)

            p1 = lambda x: isclass(x) and issubclass(x, BasePlugin)  # noqa
            p2 = lambda x: x is not BasePlugin  # noqa
            predicate = lambda x: p1(x) and p2(x)  # noqa
            plugins = getmembers(m, predicate)

            for name, Plugin in plugins:
                instance = Plugin(*self.init_args, **self.init_kwargs)
                instance.register(self)
                self.logger.debug(u"Registered Component: {0:s}".format(instance))
                if name not in self.plugins:
                    self.plugins[name] = set()
                self.plugins[name].add(instance)

            msg = u"Loaded plugin: {0:s}".format(name)
            self.logger.info(msg)
            return msg
        except Exception, e:
            msg = u"Could not load plugin: {0:s} Error: {1:s}".format(name, e)
            self.logger.error(msg)
            self.logger.error(format_exc())
            return msg

    def unload(self, name):
        if name in self.plugins:
            instances = self.plugins[name]
            for instance in instances:
                kill(instance)
                self.logger.debug(u"Unregistered Component: {0:s}".format(instance))
                if hasattr(instance, "cleanup"):
                    instance.cleanup()
                    self.logger.debug(u"Cleaned up Component: {0:s}".format(instance))
            del self.plugins[name]

            msg = u"Unloaded plugin: {0:s}".format(name)
            self.logger.info(msg)
            return msg
        else:
            msg = u"Not unloading unloaded plugin: {0:s}".format(name)
            self.logger.warn(msg)
            return msg
