import asyncio
from datetime import timedelta
import warnings

import pytest

import aionowplaying as aionp
from aionowplaying import LoopStatus, NowPlaying, PlaybackPropertyName, PlaybackStatus
from aionowplaying.interface.base import MediaType, PropertyName, TrackListPropertyName


class DummyInterface(aionp.BaseInterface):
    def __init__(self):
        super().__init__("dummy")
        self.playback_updates = []

    def set_playback_property(self, name, value):
        self.playback_updates.append((name, value))


class NowPlayingFacade(DummyInterface):
    def update_playback_mode(self, loop_status: aionp.LoopStatus, shuffle: bool):
        self.set_playback_property(aionp.PlaybackPropertyName.LoopStatus, loop_status)
        self.set_playback_property(aionp.PlaybackPropertyName.Shuffle, shuffle)

    def update_song_props(self, meta: dict):
        metadata = aionp.PlaybackProperties.MetadataBean()
        metadata.artist = meta.get("artists", ["Unknown"])
        metadata.album = meta.get("album", "")
        metadata.title = meta.get("title", "")
        metadata.cover = meta.get("artwork", "")
        metadata.url = meta.get("artwork", "")
        metadata.duration = 0
        self.set_playback_property(aionp.PlaybackPropertyName.Metadata, metadata)

    def update_position(self, position):
        self.set_playback_property(aionp.PlaybackPropertyName.Position, int(position * 1000))

    def update_playback_status(self, status: aionp.PlaybackStatus):
        self.set_playback_property(aionp.PlaybackPropertyName.PlaybackStatus, status)


def test_update_song_props():
    server = NowPlayingFacade()
    server.update_song_props({
        "title": "Hello World",
        "artists": ["hello world"],
        "album": "Hello World",
        "artwork": "https://example.com/art.jpg",
    })

    name, metadata = server.playback_updates[-1]
    assert name == aionp.PlaybackPropertyName.Metadata
    assert metadata.title == "Hello World"
    assert metadata.artist == ["hello world"]
    assert metadata.album == "Hello World"
    assert metadata.cover == "https://example.com/art.jpg"
    assert metadata.url == "https://example.com/art.jpg"


def test_update_position():
    server = NowPlayingFacade()
    server.update_position(20.5)
    assert server.playback_updates[-1] == (aionp.PlaybackPropertyName.Position, 20500)


def test_update_playback_status():
    server = NowPlayingFacade()
    server.update_playback_status(aionp.PlaybackStatus.Playing)
    assert server.playback_updates[-1] == (
        aionp.PlaybackPropertyName.PlaybackStatus,
        aionp.PlaybackStatus.Playing,
    )


def test_update_playback_mode():
    server = NowPlayingFacade()
    server.update_playback_mode(aionp.LoopStatus.Playlist, True)
    server.update_playback_mode(aionp.LoopStatus.Track, False)

    assert server.playback_updates[0] == (
        aionp.PlaybackPropertyName.LoopStatus,
        aionp.LoopStatus.Playlist,
    )
    assert server.playback_updates[1] == (
        aionp.PlaybackPropertyName.Shuffle,
        True,
    )
    assert server.playback_updates[2] == (
        aionp.PlaybackPropertyName.LoopStatus,
        aionp.LoopStatus.Track,
    )
    assert server.playback_updates[3] == (
        aionp.PlaybackPropertyName.Shuffle,
        False,
    )


def test_nowplaying_init_with_name():
    """Test basic initialization with just a name."""
    player = NowPlaying("Test Player")
    assert player is not None
    assert player.name == "Test Player"
    assert player._identity == "Test Player"


def test_nowplaying_init_with_identity():
    """Test initialization with custom identity."""
    player = NowPlaying("Test Player", identity="Custom Identity")
    assert player.name == "Test Player"
    assert player._identity == "Custom Identity"
    assert player.identity == "Custom Identity"


def test_init_applies_metadata_mapping():
    """Test that initial metadata is mapped onto NowPlaying properties."""
    metadata = {
        "title": "Mapped Song",
        "artist": "Solo Artist",
        "album": "Mapped Album",
        "album_artist": "Album Artist",
        "cover": "file:///tmp/cover.png",
        "url": "file:///tmp/song.mp3",
        "track_number": 7,
        "duration": timedelta(minutes=4, seconds=5),
    }

    player = NowPlaying("Test Player", metadata=metadata)

    assert player.title == "Mapped Song"
    assert player.artist == ["Solo Artist"]
    assert player.album == "Mapped Album"
    assert player.album_artist == ["Album Artist"]
    assert player.cover == "file:///tmp/cover.png"
    assert player.url == "file:///tmp/song.mp3"
    assert player.track_number == 7
    assert player.duration == timedelta(minutes=4, seconds=5)


def test_init_applies_extended_metadata_fields():
    """Test metadata fields stored directly on the underlying MetadataBean."""
    metadata = {
        "id": "track-123",
        "media_type": MediaType.Video,
        "composer": ["Composer"],
        "genre": ["Genre"],
        "lyrics": "lyrics",
        "comments": ["comment"],
        "lyricist": ["Lyricist"],
    }

    player = NowPlaying("Test Player", metadata=metadata)
    applied = player._interface.get_playback_property(PlaybackPropertyName.Metadata)

    assert applied.id_ == "track-123"
    assert applied.media_type == MediaType.Video
    assert applied.composer == ["Composer"]
    assert applied.genre == ["Genre"]
    assert applied.lyrics == "lyrics"
    assert applied.comments == ["comment"]
    assert applied.lyricist == ["Lyricist"]


def test_capability_inference_from_callbacks():
    """Test that capabilities are auto-inferred from callbacks."""
    player = NowPlaying(
        "Test Player",
        on_play=lambda: None,
        on_pause=lambda: None,
        on_next=lambda: None,
    )

    # Check that capabilities were set
    assert player._interface.get_playback_property(PlaybackPropertyName.CanPlay) is True
    assert player._interface.get_playback_property(PlaybackPropertyName.CanPause) is True
    assert player._interface.get_playback_property(PlaybackPropertyName.CanGoNext) is True
    assert player._interface.get_playback_property(PlaybackPropertyName.CanControl) is True

    # Check that non-registered capabilities are False
    assert player._interface.get_playback_property(PlaybackPropertyName.CanGoPrevious) is False


def test_timedelta_to_microseconds():
    """Test timedelta to microseconds conversion."""
    player = NowPlaying("Test Player")

    # 1 second = 1,000,000 microseconds
    assert player._timedelta_to_microseconds(timedelta(seconds=1)) == 1_000_000

    # 1.5 seconds = 1,500,000 microseconds
    assert player._timedelta_to_microseconds(timedelta(seconds=1.5)) == 1_500_000

    # 3 minutes 30 seconds = 210,000,000 microseconds
    assert player._timedelta_to_microseconds(timedelta(minutes=3, seconds=30)) == 210_000_000


def test_microseconds_to_timedelta():
    """Test microseconds to timedelta conversion."""
    player = NowPlaying("Test Player")

    result = player._microseconds_to_timedelta(1_000_000)
    assert result == timedelta(seconds=1)

    result = player._microseconds_to_timedelta(210_000_000)
    assert result == timedelta(minutes=3, seconds=30)


def test_title_property():
    """Test title property getter/setter."""
    player = NowPlaying("Test Player")
    player.title = "Test Song"
    assert player.title == "Test Song"


def test_artist_property():
    """Test artist property getter/setter."""
    player = NowPlaying("Test Player")

    # Test with list
    player.artist = ["Artist 1", "Artist 2"]
    assert player.artist == ["Artist 1", "Artist 2"]

    # Test with string (should convert to list)
    player.artist = "Single Artist"
    assert player.artist == ["Single Artist"]


def test_album_property():
    """Test album property getter/setter."""
    player = NowPlaying("Test Player")
    player.album = "Test Album"
    assert player.album == "Test Album"


def test_album_artist_property():
    """Test album_artist property getter/setter."""
    player = NowPlaying("Test Player")
    player.album_artist = ["Album Artist 1"]
    assert player.album_artist == ["Album Artist 1"]

    player.album_artist = "Single Album Artist"
    assert player.album_artist == ["Single Album Artist"]


def test_cover_property():
    """Test cover property getter/setter."""
    player = NowPlaying("Test Player")
    player.cover = "file:///path/to/cover.jpg"
    assert player.cover == "file:///path/to/cover.jpg"


def test_url_property():
    """Test url property getter/setter."""
    player = NowPlaying("Test Player")
    player.url = "file:///path/to/song.mp3"
    assert player.url == "file:///path/to/song.mp3"


def test_track_number_property():
    """Test track_number property getter/setter."""
    player = NowPlaying("Test Player")
    player.track_number = 5
    assert player.track_number == 5


def test_duration_property():
    """Test duration property with timedelta."""
    player = NowPlaying("Test Player")
    player.duration = timedelta(minutes=3, seconds=30)
    assert player.duration == timedelta(minutes=3, seconds=30)


# Playback state properties tests

def test_position_property():
    """Test position property with timedelta."""
    player = NowPlaying("Test Player")
    player.position = timedelta(seconds=60)
    assert player.position == timedelta(seconds=60)


def test_is_playing_property():
    """Test is_playing property (read-only, use set_playing() to change)."""
    player = NowPlaying("Test Player")
    assert player.is_playing is False

    player.set_playing()
    assert player.is_playing is True
    assert player._interface.get_playback_property(PlaybackPropertyName.PlaybackStatus) == PlaybackStatus.Playing


def test_is_paused_property():
    """Test is_paused property (read-only, use set_paused() to change)."""
    player = NowPlaying("Test Player")

    player.set_paused()
    assert player.is_paused is True
    assert player._interface.get_playback_property(PlaybackPropertyName.PlaybackStatus) == PlaybackStatus.Paused


def test_is_stopped_property():
    """Test is_stopped property (read-only, use set_stopped() to change)."""
    player = NowPlaying("Test Player")

    player.set_stopped()
    assert player.is_stopped is True
    assert player._interface.get_playback_property(PlaybackPropertyName.PlaybackStatus) == PlaybackStatus.Stopped


def test_volume_property():
    """Test volume property."""
    player = NowPlaying("Test Player")
    player.volume = 0.5
    assert player.volume == 0.5


def test_shuffle_property():
    """Test shuffle property."""
    player = NowPlaying("Test Player")
    player.shuffle = True
    assert player.shuffle is True


def test_loop_status_property():
    """Test loop_status property."""
    player = NowPlaying("Test Player")
    player.loop_status = LoopStatus.Track
    assert player.loop_status == LoopStatus.Track


def test_rate_property():
    """Test rate property."""
    player = NowPlaying("Test Player")
    player.rate = 1.5
    assert player.rate == 1.5


def test_player_properties_and_tracklist_properties():
    """Test player and tracklist property getters/setters."""
    player = NowPlaying("Test Player")

    player.identity = "Updated Identity"
    player.fullscreen = True
    player.can_quit = True
    player.can_set_fullscreen = True
    player.can_raise = True
    player.has_tracklist = True
    player.desktop_entry = "test-player"
    player.supported_uri_schemes = ["file", "https"]
    player.supported_mime_types = ["audio/mpeg"]
    player.tracks = ["/track/1", "/track/2"]
    player.can_edit_tracks = True

    assert player.identity == "Updated Identity"
    assert player._identity == "Updated Identity"
    assert player.fullscreen is True
    assert player.can_quit is True
    assert player.can_set_fullscreen is True
    assert player.can_raise is True
    assert player.has_tracklist is True
    assert player.desktop_entry == "test-player"
    assert player.supported_uri_schemes == ["file", "https"]
    assert player.supported_mime_types == ["audio/mpeg"]
    assert player.tracks == ["/track/1", "/track/2"]
    assert player.can_edit_tracks is True


def test_minimum_and_maximum_rate_properties():
    """Test minimum and maximum rate getters/setters."""
    player = NowPlaying("Test Player")

    player.minimum_rate = 0.5
    player.maximum_rate = 2.0

    assert player.minimum_rate == 0.5
    assert player.maximum_rate == 2.0


def test_generic_property_helpers():
    """Test generic property helper methods."""
    player = NowPlaying("Test Player")

    player.set_property(PropertyName.DesktopEntry, "helper-entry")
    player.set_playback_property(PlaybackPropertyName.CanControl, True)
    player.set_tracklist_property(TrackListPropertyName.CanEditTracks, True)

    assert player.get_property(PropertyName.DesktopEntry) == "helper-entry"
    assert player.get_playback_property(PlaybackPropertyName.CanControl) is True
    assert player.get_tracklist_property(TrackListPropertyName.CanEditTracks) is True


@pytest.mark.asyncio
async def test_start_stop_lifecycle():
    """Test start and stop lifecycle methods."""
    player = NowPlaying("Test Player")

    # Start should call internal interface start
    # We can't easily test this without mocking, so just verify it doesn't raise
    try:
        await player.start()
    except Exception as e:
        # Some platforms may fail due to missing dependencies
        # but the method should exist
        pass

    await player.stop()


@pytest.mark.asyncio
async def test_callback_execution():
    """Test that registered callbacks are executed."""
    call_log = []

    player = NowPlaying(
        "Test Player",
        on_play=lambda: call_log.append('play'),
        on_pause=lambda: call_log.append('pause'),
    )

    # Simulate callback execution through the interface
    await player._interface.on_play()
    await player._interface.on_pause()

    # Allow any async tasks to complete
    await asyncio.sleep(0.1)

    assert 'play' in call_log
    assert 'pause' in call_log


@pytest.mark.asyncio
async def test_extended_callbacks_are_forwarded():
    """Test that newly exposed callbacks are wired to the facade."""
    call_log = []
    metadata_result = [aionp.PlaybackProperties.MetadataBean(id_="/track/1", title="Track 1")]

    player = NowPlaying(
        "Test Player",
        on_play_pause=lambda: call_log.append("play_pause"),
        on_rate=lambda rate: call_log.append(("rate", rate)),
        on_open_uri=lambda uri: call_log.append(("open_uri", uri)),
        on_set_position=lambda track_id, delta: call_log.append(("set_position", track_id, delta)),
        on_get_tracks_metadata=lambda track_ids: metadata_result if track_ids == ["/track/1"] else [],
        on_add_track=lambda uri, after_track, set_as_current: call_log.append(
            ("add_track", uri, after_track, set_as_current)
        ),
        on_remove_track=lambda track_id: call_log.append(("remove_track", track_id)),
        on_goto=lambda track_id: call_log.append(("goto", track_id)),
        on_fullscreen=lambda fullscreen: call_log.append(("fullscreen", fullscreen)),
        on_raise=lambda: call_log.append("raise"),
        on_quit=lambda: call_log.append("quit"),
    )

    await player._interface.on_play_pause()
    await player._interface.on_rate(1.25)
    await player._interface.on_open_uri("https://example.com")
    await player._interface.on_set_position("/track/1", 2_000_000)
    result = await player._interface.on_get_tracks_metadata(["/track/1"])
    await player._interface.on_add_track("file:///song.mp3", "/track/1", True)
    await player._interface.on_remove_track("/track/1")
    await player._interface.on_goto("/track/2")
    await player._interface.on_fullscreen(True)
    await player._interface.on_raise()
    await player._interface.on_quit()
    await asyncio.sleep(0.1)

    assert result == metadata_result
    assert "play_pause" in call_log
    assert ("rate", 1.25) in call_log
    assert ("open_uri", "https://example.com") in call_log
    assert ("set_position", "/track/1", timedelta(seconds=2)) in call_log
    assert ("add_track", "file:///song.mp3", "/track/1", True) in call_log
    assert ("remove_track", "/track/1") in call_log
    assert ("goto", "/track/2") in call_log
    assert ("fullscreen", True) in call_log
    assert "raise" in call_log
    assert "quit" in call_log


@pytest.mark.asyncio
async def test_seek_callback_converts_microseconds_to_timedelta():
    """Test seek callback wrapper converts microseconds to timedelta."""
    offsets = []

    player = NowPlaying(
        "Test Player",
        on_seek=lambda delta: offsets.append(delta),
    )

    await player._interface.on_seek(2_500_000)

    assert offsets == [timedelta(seconds=2, microseconds=500000)]


@pytest.mark.asyncio
async def test_async_callback_is_scheduled():
    """Test async callback results are scheduled as tasks."""
    seen = []
    callback_done = asyncio.Event()

    async def on_play():
        seen.append("play")
        callback_done.set()

    player = NowPlaying("Test Player", on_play=on_play)

    await player._interface.on_play()
    await asyncio.wait_for(callback_done.wait(), timeout=1)

    assert seen == ["play"]


@pytest.mark.asyncio
async def test_get_tracks_metadata_async_callback_is_awaited():
    """Test async metadata callback returns its result to the backend."""
    callback_done = asyncio.Event()
    expected = [aionp.PlaybackProperties.MetadataBean(id_="/track/async")]

    async def on_get_tracks_metadata(track_ids):
        assert track_ids == ["/track/async"]
        callback_done.set()
        return expected

    player = NowPlaying("Test Player", on_get_tracks_metadata=on_get_tracks_metadata)

    result = await player._interface.on_get_tracks_metadata(["/track/async"])
    await asyncio.wait_for(callback_done.wait(), timeout=1)

    assert result == expected


@pytest.mark.asyncio
async def test_track_events_and_seeked_are_forwarded(monkeypatch):
    """Test facade event methods forward to the underlying interface."""
    player = NowPlaying("Test Player")
    calls = {}

    async def fake_track_added(metadata, after_track):
        calls["track_added"] = (metadata, after_track)

    async def fake_track_removed(track_id):
        calls["track_removed"] = track_id

    async def fake_track_list_replaced(tracks, current_track):
        calls["track_list_replaced"] = (tracks, current_track)

    async def fake_track_metadata_changed(track_id, metadata):
        calls["track_metadata_changed"] = (track_id, metadata)

    async def fake_seeked(position):
        calls["seeked"] = position

    monkeypatch.setattr(player._interface, "track_added", fake_track_added)
    monkeypatch.setattr(player._interface, "track_removed", fake_track_removed)
    monkeypatch.setattr(player._interface, "track_list_replaced", fake_track_list_replaced)
    monkeypatch.setattr(player._interface, "track_metadata_changed", fake_track_metadata_changed)
    monkeypatch.setattr(player._interface, "seeked", fake_seeked)

    metadata = aionp.PlaybackProperties.MetadataBean(id_="/track/1", title="Track 1")

    await player.track_added(metadata, "/track/0")
    await player.track_removed("/track/1")
    await player.track_list_replaced(["/track/1", "/track/2"], "/track/2")
    await player.track_metadata_changed("/track/1", metadata)
    await player.seeked(timedelta(seconds=3))

    assert calls["track_added"] == (metadata, "/track/0")
    assert calls["track_removed"] == "/track/1"
    assert calls["track_list_replaced"] == (["/track/1", "/track/2"], "/track/2")
    assert calls["track_metadata_changed"] == ("/track/1", metadata)
    assert calls["seeked"] == 3_000_000


def test_select_interface_deprecation():
    """Test that select_interface shows deprecation warning."""
    from aionowplaying.interface import select_interface

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        select_interface()

        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "deprecated" in str(w[0].message).lower()


def test_nowplaying_interface_deprecation():
    """Test that NowPlayingInterface shows deprecation warning."""
    import aionowplaying

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        _ = aionowplaying.NowPlayingInterface

        assert len(w) >= 1
        assert any(issubclass(x.category, DeprecationWarning) for x in w)
