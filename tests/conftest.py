import sys
from types import ModuleType

import pytest


def _install_fake_dbus_next():
    if "dbus_next" in sys.modules:
        return

    dbus_next = ModuleType("dbus_next")

    class PropertyAccess:
        READ = "read"
        READWRITE = "readwrite"

    class Variant:
        def __init__(self, signature, value):
            self.signature = signature
            self.value = value

        def __repr__(self):
            return f"Variant({self.signature!r}, {self.value!r})"

    dbus_next.PropertyAccess = PropertyAccess
    dbus_next.Variant = Variant

    aio = ModuleType("dbus_next.aio")

    class MessageBus:
        def __init__(self):
            self.exported = []
            self.requested_name = None
            self.disconnected = False

        async def connect(self):
            return self

        def export(self, path, iface):
            self.exported.append((path, iface))

        async def request_name(self, name):
            self.requested_name = name

        async def wait_for_disconnect(self):
            return None

        def disconnect(self):
            self.disconnected = True

    aio.MessageBus = MessageBus

    service = ModuleType("dbus_next.service")

    class ServiceInterface:
        def __init__(self, name):
            self._service_name = name
            self.emitted = []

        def emit_properties_changed(self, changed):
            self.emitted.append(changed)

    def dbus_property(*_args, **_kwargs):
        def decorator(func):
            return property(func)
        return decorator

    def method(*_args, **_kwargs):
        def decorator(func):
            return func
        return decorator

    def signal(*_args, **_kwargs):
        def decorator(func):
            return func
        return decorator

    service.ServiceInterface = ServiceInterface
    service.dbus_property = dbus_property
    service.method = method
    service.signal = signal

    sys.modules["dbus_next"] = dbus_next
    sys.modules["dbus_next.aio"] = aio
    sys.modules["dbus_next.service"] = service


_install_fake_dbus_next()


@pytest.fixture(autouse=True)
def fake_dbus_next():
    yield
