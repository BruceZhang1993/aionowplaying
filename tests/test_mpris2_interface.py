import asyncio

import pytest

from aionowplaying.interface.base import PlaybackProperties, PlaybackPropertyName, PlaybackStatus, LoopStatus, PropertyName
from aionowplaying.interface import mpris2


@pytest.mark.asyncio
async def test_dbus_mapper_and_player_set_property():
    meta = PlaybackProperties.MetadataBean()
    meta.title = "Song"
    meta.artist = ["Artist"]

    mapped = mpris2.DBusBeanMapper.metadata(meta)
    assert mapped["xesam:title"].value == "Song"
    assert mapped["xesam:artist"].value == ["Artist"]

    player = mpris2.MprisPlayerServiceInterface("org.mpris.MediaPlayer2.Player")
    player.set_property(PlaybackPropertyName.Position.value, 123)
    assert player.emitted == []

    player.set_property(PlaybackPropertyName.Metadata.value, meta)
    assert player.emitted
    assert PlaybackPropertyName.Metadata.value in player.emitted[-1]
    assert "mpris:trackid" in player.emitted[-1][PlaybackPropertyName.Metadata.value]


@pytest.mark.asyncio
async def test_loop_status_respects_can_control():
    called = {"count": 0}

    class It:
        async def on_loop_status(self, status):
            called["count"] += 1

    player = mpris2.MprisPlayerServiceInterface("org.mpris.MediaPlayer2.Player", it=It())
    await type(player).loop_status.fset(player, LoopStatus.Playlist.value)
    assert called["count"] == 0
    assert player._properties.LoopStatus == LoopStatus.None_

    player._properties.CanControl = True
    await type(player).loop_status.fset(player, LoopStatus.Track.value)
    assert called["count"] == 1
    assert player._properties.LoopStatus == LoopStatus.Track


@pytest.mark.asyncio
async def test_player_methods_respect_flags():
    called = {"play": 0, "pause": 0}

    class It:
        async def on_play(self):
            called["play"] += 1

        async def on_pause(self):
            called["pause"] += 1

    player = mpris2.MprisPlayerServiceInterface("org.mpris.MediaPlayer2.Player", it=It())
    await player.play()
    await player.pause()
    assert called == {"play": 0, "pause": 0}

    player._properties.CanPlay = True
    player._properties.CanPause = True
    await player.play()
    await player.pause()
    assert called == {"play": 1, "pause": 1}


@pytest.mark.asyncio
async def test_service_interface_raise_and_quit():
    called = {"raise": 0, "quit": 0}

    class It:
        async def on_raise(self):
            called["raise"] += 1

        async def on_quit(self):
            called["quit"] += 1

    service = mpris2.MprisServiceInterface("org.mpris.MediaPlayer2", it=It())
    await service.raise_()
    await service.quit()
    assert called == {"raise": 0, "quit": 0}

    service._properties.CanRaise = True
    service._properties.CanQuit = True
    await service.raise_()
    await service.quit()
    assert called == {"raise": 1, "quit": 1}


@pytest.mark.asyncio
async def test_tracklist_properties():
    tracklist = mpris2.MprisTracklistServiceInterface("org.mpris.MediaPlayer2.TrackList")
    tracklist.set_property("Tracks", ["t1", "t2"])
    tracklist.set_property("CanEditTracks", True)

    assert tracklist.get_property("Tracks") == ["t1", "t2"]
    assert tracklist.get_property("CanEditTracks") is True


@pytest.mark.asyncio
async def test_mpris2_interface_start_stop_and_getters():
    it = mpris2.Mpris2Interface("player")

    it.set_property(PropertyName.CanQuit, True)
    it.set_playback_property(PlaybackPropertyName.PlaybackStatus, PlaybackStatus.Playing)

    assert it.get_property(PropertyName.CanQuit) is True
    assert it.get_playback_property(PlaybackPropertyName.PlaybackStatus) == PlaybackStatus.Playing

    await it.start()
    assert it.dbus is not None
    assert it.dbus.requested_name == "org.mpris.MediaPlayer2.player"

    await it.seeked(123)

    await it.stop()
    assert it.dbus.disconnected is True

    it2 = mpris2.Mpris2Interface("player2")
    await it2.stop()
