import importlib
import sys
from typing import Type

from aionowplaying.interface.base import BaseInterface

INTERFACES_BY_SYSTEM = {
    'linux': 'aionowplaying.interface.mpris2.Mpris2Interface',
    'win32': 'aionowplaying.interface.windows.WindowsInterface',
    'darwin': 'aionowplaying.interface.macos.MacOSInterface',
}


def _select_interface_impl(system: str = None) -> Type[BaseInterface]:
    """Internal implementation of select_interface without deprecation warning."""
    if system is None:
        system = sys.platform
    name = INTERFACES_BY_SYSTEM.get(system, 'aionowplaying.interface.base.BaseInterface')
    mod = name.rsplit('.', 1)
    return getattr(importlib.import_module(mod[0]), mod[1])


def select_interface(system: str = None) -> Type[BaseInterface]:
    """Select the appropriate interface for the current platform."""
    return _select_interface_impl(system)
