import sys
from typing import Type, Union

from aionowplaying.interface.base import BaseInterface
from aionowplaying.interface.mpris2 import Mpris2Interface

INTERFACES_BY_SYSTEM = {'linux': Mpris2Interface}


def select_interface(system: str = None) -> Type[BaseInterface]:
    if system is None:
        system = sys.platform
    return INTERFACES_BY_SYSTEM.get(system, BaseInterface)
