import asyncio
import sys

import pytest

from aionowplaying.interface.base import PlaybackProperties, PlaybackPropertyName, PlaybackStatus, LoopStatus, \
    PropertyName, TrackListPropertyName


pytestmark = pytest.mark.skipif(sys.platform != "linux", reason="Linux-only tests")

if sys.platform == "linux":
    mpris2 = pytest.importorskip("aionowplaying.interface.mpris2")
else:
    mpris2 = None


class _FakeBus:
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
    assert player.get_property(PlaybackPropertyName.Position.value) == 123

    player.set_property(PlaybackPropertyName.Metadata.value, meta)
    assert player.get_property(PlaybackPropertyName.Metadata.value) == meta


def test_dbus_mapper_track_id_is_valid_object_path():
    no_track = "/org/mpris/MediaPlayer2/TrackList/NoTrack"

    mapped_default = mpris2.DBusBeanMapper.metadata(PlaybackProperties.MetadataBean())
    assert mapped_default["mpris:trackid"].signature == "o"
    assert mapped_default["mpris:trackid"].value == no_track

    mapped_path = mpris2.DBusBeanMapper.metadata(PlaybackProperties.MetadataBean(id_="/track/1"))
    assert mapped_path["mpris:trackid"].value == "/track/1"

    mapped_text = mpris2.DBusBeanMapper.metadata(PlaybackProperties.MetadataBean(id_="track-123"))
    assert mapped_text["mpris:trackid"].value.startswith("/org/mpris/MediaPlayer2/TrackList/")
    assert "-" not in mapped_text["mpris:trackid"].value


@pytest.mark.asyncio
async def test_loop_status_respects_can_control():
    called = {"count": 0}

    class It:
        async def on_loop_status(self, status):
            called["count"] += 1

    player = mpris2.MprisPlayerServiceInterface("org.mpris.MediaPlayer2.Player", it=It())
    if not hasattr(type(player).loop_status, "fset"):
        pytest.skip("dbus_fast dbus_property does not expose fset on this platform")
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
    await type(player).play.__wrapped__(player)
    await type(player).pause.__wrapped__(player)
    assert called == {"play": 0, "pause": 0}

    player._properties.CanPlay = True
    player._properties.CanPause = True
    await type(player).play.__wrapped__(player)
    await type(player).pause.__wrapped__(player)
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
    await type(service).raise_.__wrapped__(service)
    await type(service).quit.__wrapped__(service)
    assert called == {"raise": 0, "quit": 0}

    service._properties.CanRaise = True
    service._properties.CanQuit = True
    await type(service).raise_.__wrapped__(service)
    await type(service).quit.__wrapped__(service)
    assert called == {"raise": 1, "quit": 1}


@pytest.mark.asyncio
async def test_tracklist_properties():
    tracklist = mpris2.MprisTracklistServiceInterface("org.mpris.MediaPlayer2.TrackList")
    tracklist.set_property("Tracks", ["a", "track-123", "/track/1"])
    tracklist.set_property("CanEditTracks", True)

    assert tracklist.get_property("Tracks") == [
        "/org/mpris/MediaPlayer2/TrackList/a",
        "/org/mpris/MediaPlayer2/TrackList/track_123",
        "/track/1",
    ]
    assert tracklist.get_property("CanEditTracks") is True


def test_tracklist_set_property_emits_properties_changed(monkeypatch):
    tracklist = mpris2.MprisTracklistServiceInterface("org.mpris.MediaPlayer2.TrackList")
    emitted = []

    def capture(*args):
        emitted.append(args)

    monkeypatch.setattr(tracklist, "emit_properties_changed", capture)

    tracklist.set_property(TrackListPropertyName.CanEditTracks.value, True)
    tracklist.set_property(TrackListPropertyName.Tracks.value, ["t1", "t2"])

    assert emitted == [
        ({TrackListPropertyName.CanEditTracks.value: True},),
        ({}, [TrackListPropertyName.Tracks.value]),
    ]


@pytest.mark.asyncio
async def test_mpris2_start_exports_tracklist_bus():
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(mpris2, "MessageBus", _FakeBus)
    it = mpris2.Mpris2Interface("player")

    assert it.get_property(PropertyName.HasTrackList) is True

    await it.start()

    exported_paths = [entry[0] for entry in it.dbus.exported]
    exported_ifaces = [entry[1] for entry in it.dbus.exported]
    assert exported_paths.count("/org/mpris/MediaPlayer2") == 4
    assert any(isinstance(iface, mpris2.MprisTracklistServiceInterface) for iface in exported_ifaces)
    assert any(isinstance(iface, mpris2.MprisPlaylistsServiceInterface) for iface in exported_ifaces)
    assert it.get_property(PropertyName.HasTrackList) is True
    monkeypatch.undo()


@pytest.mark.asyncio
async def test_mpris2_interface_start_stop_and_getters():
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(mpris2, "MessageBus", _FakeBus)
    it = mpris2.Mpris2Interface("player")

    it.set_property(PropertyName.CanQuit, True)
    it.set_playback_property(PlaybackPropertyName.PlaybackStatus, PlaybackStatus.Playing)
    it.set_tracklist_property(TrackListPropertyName.Tracks, ["a", "b"])

    assert it.get_property(PropertyName.CanQuit) is True
    assert it.get_playback_property(PlaybackPropertyName.PlaybackStatus) == PlaybackStatus.Playing
    assert it.get_tracklist_property(TrackListPropertyName.Tracks) == [
        "/org/mpris/MediaPlayer2/TrackList/a",
        "/org/mpris/MediaPlayer2/TrackList/b",
    ]

    await it.start()
    assert it.dbus is not None
    assert it.dbus.requested_name == "org.mpris.MediaPlayer2.player"

    await it.seeked(123)

    await it.stop()
    assert it.dbus.disconnected is True

    it2 = mpris2.Mpris2Interface("player2")
    await it2.stop()
    monkeypatch.undo()


@pytest.mark.asyncio
async def test_mpris2_tracklist_signal_bridge():
    it = mpris2.Mpris2Interface("player")
    emitted = []

    async def fake_track_added(metadata, after_track):
        emitted.append(("added", metadata, after_track))

    async def fake_track_removed(track_id):
        emitted.append(("removed", track_id))

    async def fake_track_list_replaced(tracks, current_track):
        emitted.append(("replaced", tracks, current_track))

    async def fake_track_metadata_changed(track_id, metadata):
        emitted.append(("changed", track_id, metadata))

    it._tracklist_bus.track_added = fake_track_added
    it._tracklist_bus.track_removed = fake_track_removed
    it._tracklist_bus.track_list_replaced = fake_track_list_replaced
    it._tracklist_bus.track_metadata_changed = fake_track_metadata_changed

    metadata = PlaybackProperties.MetadataBean(id_="/track/1", title="Song")
    await it.track_added(metadata, "after-1")
    await it.track_removed("track-123")
    await it.track_list_replaced(["a", "/track/1"], "current-1")
    await it.track_metadata_changed("track-123", metadata)

    assert emitted[0][0] == "added"
    assert emitted[0][1]["mpris:trackid"].signature == "o"
    assert emitted[0][1]["xesam:title"].value == "Song"
    assert emitted[0][2] == "/org/mpris/MediaPlayer2/TrackList/after_1"
    assert emitted[1] == ("removed", "/org/mpris/MediaPlayer2/TrackList/track_123")
    assert emitted[2] == (
        "replaced",
        ["/org/mpris/MediaPlayer2/TrackList/a", "/track/1"],
        "/org/mpris/MediaPlayer2/TrackList/current_1",
    )
    assert emitted[3][0] == "changed"
    assert emitted[3][1] == "/org/mpris/MediaPlayer2/TrackList/track_123"
    assert emitted[3][2]["mpris:trackid"].signature == "o"
    assert emitted[3][2]["xesam:title"].value == "Song"


def test_tracklist_signals_can_be_called_directly():
    it = mpris2.Mpris2Interface("player")
    no_track = "/org/mpris/MediaPlayer2/TrackList/NoTrack"
    metadata = PlaybackProperties.MetadataBean(id_="/track/1", title="Song")
    mapped = mpris2.DBusBeanMapper.metadata(metadata)

    assert it._tracklist_bus.track_added(mapped, no_track) == (mapped, no_track)
    assert it._tracklist_bus.track_removed("/track/1") == "/track/1"
    assert it._tracklist_bus.track_list_replaced(["/track/1"], "/track/1") == (
        ["/track/1"],
        "/track/1",
    )
    assert it._tracklist_bus.track_metadata_changed("/track/1", mapped) == (
        "/track/1",
        mapped,
    )


def _get_dbus_prop(obj, name):
    prop = getattr(type(obj), name)
    if not hasattr(prop, "fget"):
        pytest.skip("dbus_fast dbus_property does not expose fget on this platform")
    return prop.fget(obj)


async def _set_dbus_prop(obj, name, value):
    prop = getattr(type(obj), name)
    if not hasattr(prop, "fset"):
        pytest.skip("dbus_fast dbus_property does not expose fset on this platform")
    await prop.fset(obj, value)


@pytest.mark.asyncio
async def test_player_properties_and_methods_more_coverage():
    calls = {
        "rate": 0,
        "shuffle": 0,
        "volume": 0,
        "loop": 0,
        "seek": 0,
        "set_position": 0,
        "open_uri": 0,
        "next": 0,
        "previous": 0,
        "play_pause": 0,
        "stop": 0,
    }

    class It:
        async def on_rate(self, _):
            calls["rate"] += 1

        async def on_shuffle(self, _):
            calls["shuffle"] += 1

        async def on_volume(self, _):
            calls["volume"] += 1

        async def on_loop_status(self, _):
            calls["loop"] += 1

        async def on_seek(self, _):
            calls["seek"] += 1

        async def on_set_position(self, _, __):
            calls["set_position"] += 1

        async def on_open_uri(self, _):
            calls["open_uri"] += 1

        async def on_next(self):
            calls["next"] += 1

        async def on_previous(self):
            calls["previous"] += 1

        async def on_play_pause(self):
            calls["play_pause"] += 1

        async def on_stop(self):
            calls["stop"] += 1

    player = mpris2.MprisPlayerServiceInterface("org.mpris.MediaPlayer2.Player", it=It())

    assert _get_dbus_prop(player, "playback_status") == PlaybackStatus.Stopped.value
    assert _get_dbus_prop(player, "loop_status") == LoopStatus.None_.value
    assert _get_dbus_prop(player, "rate") == 1.0
    assert _get_dbus_prop(player, "shuffle") is False
    assert isinstance(_get_dbus_prop(player, "metadata"), dict)
    assert _get_dbus_prop(player, "volume") == 1.0
    assert _get_dbus_prop(player, "position") == 0
    assert _get_dbus_prop(player, "minimum_rate") == 1.0
    assert _get_dbus_prop(player, "maximum_rate") == 1.0
    assert _get_dbus_prop(player, "can_go_next") is False
    assert _get_dbus_prop(player, "can_go_previous") is False
    assert _get_dbus_prop(player, "can_play") is False
    assert _get_dbus_prop(player, "can_pause") is False
    assert _get_dbus_prop(player, "can_seek") is False
    assert _get_dbus_prop(player, "can_control") is False

    await _set_dbus_prop(player, "rate", 1.25)
    assert calls["rate"] == 1

    await _set_dbus_prop(player, "shuffle", True)
    await _set_dbus_prop(player, "volume", 0.5)
    await _set_dbus_prop(player, "loop_status", LoopStatus.Track.value)
    assert calls["shuffle"] == 0
    assert calls["volume"] == 0
    assert calls["loop"] == 0

    player._properties.CanControl = True
    await _set_dbus_prop(player, "shuffle", True)
    await _set_dbus_prop(player, "volume", 0.5)
    await _set_dbus_prop(player, "loop_status", LoopStatus.Track.value)
    assert calls["shuffle"] == 1
    assert calls["volume"] == 1
    assert calls["loop"] == 1

    await type(player).seek.__wrapped__(player, 123)
    assert calls["seek"] == 0
    player._properties.CanSeek = True
    await type(player).seek.__wrapped__(player, 456)
    assert calls["seek"] == 1

    await type(player).set_position.__wrapped__(player, "/track/1", 100)
    assert calls["set_position"] == 1

    await type(player).open_uri.__wrapped__(player, "https://example.com")
    assert calls["open_uri"] == 1

    player._properties.CanGoNext = False
    player._properties.CanGoPrevious = False
    player._properties.CanPause = False
    player._properties.CanControl = False

    await type(player).next.__wrapped__(player)
    await type(player).previous.__wrapped__(player)
    await type(player).play_pause.__wrapped__(player)
    await type(player).stop.__wrapped__(player)
    assert calls["next"] == 0
    assert calls["previous"] == 0
    assert calls["play_pause"] == 0
    assert calls["stop"] == 0

    player._properties.CanGoNext = True
    player._properties.CanGoPrevious = True
    player._properties.CanPause = True
    player._properties.CanControl = True

    await type(player).next.__wrapped__(player)
    await type(player).previous.__wrapped__(player)
    await type(player).play_pause.__wrapped__(player)
    await type(player).stop.__wrapped__(player)
    assert calls["next"] == 1
    assert calls["previous"] == 1
    assert calls["play_pause"] == 1
    assert calls["stop"] == 1


@pytest.mark.asyncio
async def test_service_interface_fullscreen_setter():
    called = {"fullscreen": 0}

    class It:
        async def on_fullscreen(self, _):
            called["fullscreen"] += 1

    service = mpris2.MprisServiceInterface("org.mpris.MediaPlayer2", it=It())
    await _set_dbus_prop(service, "fullscreen", True)
    assert called["fullscreen"] == 0
    assert service._properties.Fullscreen is False

    service._properties.CanSetFullscreen = True
    await _set_dbus_prop(service, "fullscreen", True)
    assert called["fullscreen"] == 1
    assert service._properties.Fullscreen is True

    assert _get_dbus_prop(service, "fullscreen") is True
    assert _get_dbus_prop(service, "can_quit") is False
    assert _get_dbus_prop(service, "can_set_fullscreen") is True
    assert _get_dbus_prop(service, "has_track_list") is False
    assert _get_dbus_prop(service, "can_raise") is False
    assert _get_dbus_prop(service, "identity") == ""
    assert _get_dbus_prop(service, "desktop_entry") == ""
    assert _get_dbus_prop(service, "supported_uri_schemes") == []
    assert _get_dbus_prop(service, "supported_mime_types") == []


def test_tracklist_dbus_properties():
    tracklist = mpris2.MprisTracklistServiceInterface("org.mpris.MediaPlayer2.TrackList")
    assert _get_dbus_prop(tracklist, "can_edit_tracks") is False
    assert _get_dbus_prop(tracklist, "tracks") == []


@pytest.mark.asyncio
async def test_tracklist_methods_dispatch_to_interface():
    calls = {
        "metadata": None,
        "add": None,
        "remove": None,
        "goto": None,
    }

    class It:
        async def on_get_tracks_metadata(self, track_ids):
            calls["metadata"] = track_ids
            return [PlaybackProperties.MetadataBean(id_="/track/1", title="Song")]

        async def on_add_track(self, uri, after_track, set_as_current):
            calls["add"] = (uri, after_track, set_as_current)

        async def on_remove_track(self, track_id):
            calls["remove"] = track_id

        async def on_goto(self, track_id):
            calls["goto"] = track_id

    tracklist = mpris2.MprisTracklistServiceInterface("org.mpris.MediaPlayer2.TrackList", it=It())
    tracklist._properties.CanEditTracks = True

    metadata = await type(tracklist).get_tracks_metadata.__wrapped__(tracklist, ["/track/1"])
    await type(tracklist).add_track.__wrapped__(
        tracklist,
        "file:///song.mp3",
        "/org/mpris/MediaPlayer2/TrackList/NoTrack",
        True,
    )
    await type(tracklist).remove_track.__wrapped__(tracklist, "/track/1")
    await type(tracklist).go_to.__wrapped__(tracklist, "/track/1")

    assert calls["metadata"] == ["/track/1"]
    assert calls["add"] == ("file:///song.mp3", "/org/mpris/MediaPlayer2/TrackList/NoTrack", True)
    assert calls["remove"] == "/track/1"
    assert calls["goto"] == "/track/1"
    assert metadata[0]["mpris:trackid"].signature == "o"


@pytest.mark.asyncio
async def test_tracklist_edit_methods_respect_can_edit_tracks():
    calls = {
        "add": 0,
        "remove": 0,
    }

    class It:
        async def on_add_track(self, uri, after_track, set_as_current):
            calls["add"] += 1

        async def on_remove_track(self, track_id):
            calls["remove"] += 1

    tracklist = mpris2.MprisTracklistServiceInterface("org.mpris.MediaPlayer2.TrackList", it=It())

    await type(tracklist).add_track.__wrapped__(
        tracklist,
        "file:///song.mp3",
        "/org/mpris/MediaPlayer2/TrackList/NoTrack",
        True,
    )
    await type(tracklist).remove_track.__wrapped__(tracklist, "/track/1")

    assert calls == {"add": 0, "remove": 0}


@pytest.mark.asyncio
async def test_fullscreen_setter_when_can_set_fullscreen_false():
    """Test that fullscreen setter does nothing when CanSetFullscreen is False."""
    called = {"fullscreen": 0}

    class It:
        async def on_fullscreen(self, _):
            called["fullscreen"] += 1

    service = mpris2.MprisServiceInterface("org.mpris.MediaPlayer2", it=It())
    # CanSetFullscreen is False by default
    assert service._properties.CanSetFullscreen is False

    # Attempt to set fullscreen should be ignored
    await _set_dbus_prop(service, "fullscreen", True)

    # Callback should not be called
    assert called["fullscreen"] == 0
    # Property should remain False
    assert service._properties.Fullscreen is False
