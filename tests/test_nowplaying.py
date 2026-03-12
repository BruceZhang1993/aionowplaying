import pytest

import aionowplaying as aionp
from aionowplaying import NowPlaying, PlaybackPropertyName, PlaybackStatus, LoopStatus
from datetime import timedelta


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
