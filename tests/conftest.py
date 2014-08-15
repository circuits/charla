# Module:   conftest
# Date:     13th August 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Test Configuration and Fixtures"""


import threading
from time import sleep
from collections import deque


from pytest import fixture

from circuits import handler, BaseComponent, Debugger, Manager

from circuits.core.manager import TIMEOUT


from .client import Client
from .server import Server


class Watcher(BaseComponent):

    def init(self):
        self._lock = threading.Lock()
        self.events = deque()

    @handler(channel="*", priority=999.9)
    def _on_event(self, event, *args, **kwargs):
        with self._lock:
            self.events.append(event)

    def clear(self):
        self.events.clear()

    def wait(self, name, channel=None, timeout=6.0):
        try:
            for i in range(int(timeout / TIMEOUT)):
                if channel is None:
                    with self._lock:
                        for event in self.events:
                            if event.name == name:
                                return True
                else:
                    with self._lock:
                        for event in self.events:
                            if event.name == name and \
                                    channel in event.channels:
                                return True

                sleep(TIMEOUT)
        finally:
            self.events.clear()


class Flag(object):
    status = False


class WaitEvent(object):

    def __init__(self, manager, name, channel=None, timeout=6.0):
        if channel is None:
            channel = getattr(manager, "channel", None)

        self.timeout = timeout
        self.manager = manager

        flag = Flag()

        @handler(name, channel=channel)
        def on_event(self, *args, **kwargs):
            flag.status = True

        self.handler = self.manager.addHandler(on_event)
        self.flag = flag

    def wait(self):
        try:
            for i in range(int(self.timeout / TIMEOUT)):
                if self.flag.status:
                    return True
                sleep(TIMEOUT)
        finally:
            self.manager.removeHandler(self.handler)


@fixture(scope="session")
def manager(request):
    manager = Manager()

    def finalizer():
        manager.stop()

    request.addfinalizer(finalizer)

    waiter = WaitEvent(manager, "started")
    manager.start()
    assert waiter.wait()

    if request.config.option.verbose:
        verbose = True
    else:
        verbose = False

    Debugger(events=verbose).register(manager)

    return manager


@fixture
def watcher(request, manager):
    watcher = Watcher().register(manager)

    def finalizer():
        waiter = WaitEvent(manager, "unregistered")
        watcher.unregister()
        waiter.wait()

    request.addfinalizer(finalizer)

    return watcher


@fixture
def server(request):
    return Server()


@fixture
def client(request, manager, watcher, server):
    client = Client(server.host, server.port)

    client.register(manager)
    watcher.wait("ready")

    def finalizer():
        client.unregister()

    request.addfinalizer(finalizer)

    return client
