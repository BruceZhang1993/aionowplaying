import asyncio
import importlib

import pytest

from aionowplaying.interface.base import PlaybackProperties, PlaybackPropertyName, PlaybackStatus
from tests.fake_modules import install_fake_macos


def _import_macos_module():
    install_fake_macos()
    module = importlib.import_module("aionowplaying.interface.macos")
    importlib.reload(module)
    return module


@pytest.mark.asyncio
async def test_create_handler_executes_task():
    macos = _import_macos_module()
    called = {"count": 0}

    async def handler():
        called["count"] += 1

    wrapped = macos.create_handler(None, handler)
    wrapped(None)
    await asyncio.sleep(0)
    assert called["count"] == 1


def test_set_playback_properties_metadata_and_status():
    macos = _import_macos_module()
    it = macos.MacOSInterface("test")

    meta = PlaybackProperties.MetadataBean()
    meta.title = "Song"
    meta.artist = ["Artist1", "Artist2"]
    meta.album = "Album"

    it.set_playback_property(PlaybackPropertyName.Metadata, meta)
    info = it.info_center.nowPlayingInfo()

    assert info[macos.MPMediaItemPropertyTitle] == "Song"
    assert info[macos.MPMediaItemPropertyArtist] == "Artist1, Artist2"
    assert info[macos.MPMediaItemPropertyAlbumTitle] == "Album"

    it.set_playback_property(PlaybackPropertyName.Position, 5_000_000)
    it.set_playback_property(PlaybackPropertyName.Duration, 30_000_000)

    info = it.info_center.nowPlayingInfo()
    assert info[macos.MPNowPlayingInfoPropertyElapsedPlaybackTime] == 5
    assert info[macos.MPMediaItemPropertyPlaybackDuration] == 30

    it.set_playback_property(PlaybackPropertyName.Rate, 1.25)
    info = it.info_center.nowPlayingInfo()
    assert info[macos.MPNowPlayingInfoPropertyPlaybackRate] == 1.25

    it.set_playback_property(PlaybackPropertyName.PlaybackStatus, PlaybackStatus.Paused)
    info = it.info_center.nowPlayingInfo()
    assert info[macos.MPNowPlayingInfoPropertyPlaybackRate] == 0
    assert it.info_center.playback_state == macos.MPMusicPlaybackStatePaused

    it.set_playback_property(PlaybackPropertyName.PlaybackStatus, PlaybackStatus.Playing)
    assert it.info_center.playback_state == macos.MPMusicPlaybackStatePlaying


def test_get_playback_property():
    macos = _import_macos_module()
    it = macos.MacOSInterface("test")

    it.set_playback_property(PlaybackPropertyName.Position, 2_000_000)
    it.set_playback_property(PlaybackPropertyName.Rate, 1.5)

    assert it.get_playback_property(PlaybackPropertyName.Position) == 2
    assert it.get_playback_property(PlaybackPropertyName.Rate) == 1.5
