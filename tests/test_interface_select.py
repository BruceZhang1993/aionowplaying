import sys
from types import ModuleType

from aionowplaying.interface import select_interface


def _install_module(path: str, class_name: str):
    module = ModuleType(path)

    class Dummy:
        pass

    Dummy.__name__ = class_name
    setattr(module, class_name, Dummy)
    sys.modules[path] = module
    return Dummy


def test_select_interface_by_system():
    # Store original modules to restore after test
    original_modules = {}
    for path in ["aionowplaying.interface.mpris2", "aionowplaying.interface.windows", "aionowplaying.interface.macos"]:
        original_modules[path] = sys.modules.get(path)

    try:
        linux_cls = _install_module("aionowplaying.interface.mpris2", "Mpris2Interface")
        win_cls = _install_module("aionowplaying.interface.windows", "WindowsInterface")
        mac_cls = _install_module("aionowplaying.interface.macos", "MacOSInterface")

        assert select_interface("linux") is linux_cls
        assert select_interface("win32") is win_cls
        assert select_interface("darwin") is mac_cls
    finally:
        # Restore original modules
        for path, original in original_modules.items():
            if original is None:
                sys.modules.pop(path, None)
            else:
                sys.modules[path] = original


def test_select_interface_fallback_to_base():
    from aionowplaying.interface.base import BaseInterface

    assert select_interface("unknown") is BaseInterface
