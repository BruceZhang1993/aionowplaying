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
    # Clean up all aionowplaying modules first to ensure fresh state
    for mod_name in list(sys.modules.keys()):
        if mod_name.startswith("aionowplaying"):
            sys.modules.pop(mod_name, None)

    # Import the interface module fresh
    import aionowplaying.interface as interface

    # When importing a submodule, Python also imports the parent package.
    # We need to pop it again so it gets re-imported after the monkeypatch.
    sys.modules.pop("aionowplaying", None)

    # Monkeypatch select_interface to return None
    monkeypatch.setattr(interface, "select_interface", lambda: None)

    # With the new __getattr__ implementation, accessing NowPlayingInterface
    # will call select_interface() and return None (with a deprecation warning)
    import aionowplaying
    with pytest.warns(DeprecationWarning):
        result = aionowplaying.NowPlayingInterface
    assert result is None

    # Clean up and restore normal behavior
    monkeypatch.undo()
    for mod_name in list(sys.modules.keys()):
        if mod_name.startswith("aionowplaying"):
            sys.modules.pop(mod_name, None)
    importlib.import_module("aionowplaying")
