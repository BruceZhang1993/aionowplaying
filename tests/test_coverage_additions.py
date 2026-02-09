import importlib
import sys

import pytest

from aionowplaying.interface.base import BaseInterface, LoopStatus


@pytest.mark.asyncio
async def test_base_interface_noop_methods_are_callable():
    it = BaseInterface("base")

    await it.start()
    await it.stop()

    await it.on_fullscreen(True)
    await it.on_raise()
    await it.on_quit()
    await it.on_loop_status(LoopStatus.Playlist)
    await it.on_rate(1.25)
    await it.on_shuffle(True)
    await it.on_volume(0.5)
    await it.on_next()
    await it.on_previous()
    await it.on_pause()
    await it.on_play()
    await it.on_stop()
    await it.on_seek(123)
    await it.on_open_uri("https://example.com")
    await it.on_set_position("track", 456)
    await it.seeked(789)


def test_init_raises_when_no_interface(monkeypatch):
    import aionowplaying.interface as interface

    monkeypatch.setattr(interface, "select_interface", lambda: None)
    sys.modules.pop("aionowplaying", None)

    with pytest.raises(TypeError):
        importlib.import_module("aionowplaying")

    monkeypatch.undo()
    sys.modules.pop("aionowplaying", None)
    importlib.import_module("aionowplaying")
