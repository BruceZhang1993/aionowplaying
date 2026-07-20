from datetime import timedelta
from typing import Any, Callable
import asyncio

from aionowplaying.interface import _select_interface_impl
from aionowplaying.interface.base import (
    BaseInterface,
    LoopStatus,
    PlaybackProperties,
    PlaybackPropertyName,
    PlaybackStatus,
    PlaylistBean,
    PlaylistPropertyName,
    PropertyName,
    TrackListPropertyName,
)


class NowPlaying:
    """
    Simplified interface for Now Playing integration.

    Example:
        player = NowPlaying("My Player")
        player.title = "Song Name"
        player.artist = ["Artist"]
        await player.start()
    """

    def __init__(
        self,
        name: str,
        identity: str | None = None,
        metadata: dict[str, Any] | None = None,
        on_play: Callable[[], Any] | None = None,
        on_pause: Callable[[], Any] | None = None,
        on_next: Callable[[], Any] | None = None,
        on_previous: Callable[[], Any] | None = None,
        on_seek: Callable[[timedelta], Any] | None = None,
        on_stop: Callable[[], Any] | None = None,
        on_volume: Callable[[float], Any] | None = None,
        on_shuffle: Callable[[bool], Any] | None = None,
        on_loop: Callable[[LoopStatus], Any] | None = None,
        on_play_pause: Callable[[], Any] | None = None,
        on_rate: Callable[[float], Any] | None = None,
        on_open_uri: Callable[[str], Any] | None = None,
        on_set_position: Callable[[str, timedelta], Any] | None = None,
        on_get_tracks_metadata: Callable[[list[str]], Any] | None = None,
        on_add_track: Callable[[str, str, bool], Any] | None = None,
        on_remove_track: Callable[[str], Any] | None = None,
        on_goto: Callable[[str], Any] | None = None,
        on_fullscreen: Callable[[bool], Any] | None = None,
        on_raise: Callable[[], Any] | None = None,
        on_quit: Callable[[], Any] | None = None,
        on_activate_playlist: Callable[[str], Any] | None = None,
    ):
        self.name = name
        self._identity = identity or name
        self._interface: BaseInterface = _select_interface_impl()(name)
        self._interface.set_property(PropertyName.Identity, self._identity)

        # Store callbacks
        self._callbacks: dict[str, Callable] = {
            'on_play': on_play,
            'on_pause': on_pause,
            'on_next': on_next,
            'on_previous': on_previous,
            'on_seek': on_seek,
            'on_stop': on_stop,
            'on_volume': on_volume,
            'on_shuffle': on_shuffle,
            'on_loop': on_loop,
            'on_play_pause': on_play_pause,
            'on_rate': on_rate,
            'on_open_uri': on_open_uri,
            'on_set_position': on_set_position,
            'on_get_tracks_metadata': on_get_tracks_metadata,
            'on_add_track': on_add_track,
            'on_remove_track': on_remove_track,
            'on_goto': on_goto,
            'on_fullscreen': on_fullscreen,
            'on_raise': on_raise,
            'on_quit': on_quit,
            'on_activate_playlist': on_activate_playlist,
        }

        # Setup capabilities based on callbacks
        self._setup_capabilities()

        # Setup callback wrappers
        self._setup_callback_wrapper()

        # Apply initial metadata
        if metadata:
            self._apply_metadata(metadata)

    def _setup_capabilities(self) -> None:
        """Setup playback capabilities based on provided callbacks."""
        control_callbacks = [
            'on_play', 'on_pause', 'on_next', 'on_previous',
            'on_seek', 'on_stop', 'on_volume', 'on_shuffle', 'on_loop'
        ]

        # Set CanControl if any control callback is registered
        has_control = any(self._callbacks.get(cb) for cb in control_callbacks)
        if has_control:
            self._interface.set_playback_property(PlaybackPropertyName.CanControl, True)

        # Set specific capabilities
        callback_capability_map = {
            'on_play': PlaybackPropertyName.CanPlay,
            'on_pause': PlaybackPropertyName.CanPause,
            'on_next': PlaybackPropertyName.CanGoNext,
            'on_previous': PlaybackPropertyName.CanGoPrevious,
            'on_seek': PlaybackPropertyName.CanSeek,
        }

        for callback_name, capability in callback_capability_map.items():
            if self._callbacks.get(callback_name):
                self._interface.set_playback_property(capability, True)

    def _run_callback(self, name: str, *args) -> None:
        """Execute a callback, handling both sync and async."""
        callback = self._callbacks.get(name)
        if callback:
            result = callback(*args)
            if asyncio.iscoroutine(result):
                asyncio.create_task(result)

    async def _call_callback(self, name: str, *args) -> Any:
        """Execute a callback and await async results when a return value matters."""
        callback = self._callbacks.get(name)
        if callback is None:
            return None

        result = callback(*args)
        if asyncio.iscoroutine(result):
            return await result
        return result

    def _setup_callback_wrapper(self) -> None:
        """Set up callback wrappers to connect interface to user callbacks."""
        async def wrapped_on_fullscreen(fullscreen: bool):
            self._run_callback('on_fullscreen', fullscreen)

        async def wrapped_on_raise():
            self._run_callback('on_raise')

        async def wrapped_on_quit():
            self._run_callback('on_quit')

        async def wrapped_on_play():
            self._run_callback('on_play')

        async def wrapped_on_pause():
            self._run_callback('on_pause')

        async def wrapped_on_next():
            self._run_callback('on_next')

        async def wrapped_on_previous():
            self._run_callback('on_previous')

        async def wrapped_on_seek(offset: int):
            delta = self._microseconds_to_timedelta(offset)
            self._run_callback('on_seek', delta)

        async def wrapped_on_stop():
            self._run_callback('on_stop')

        async def wrapped_on_play_pause():
            self._run_callback('on_play_pause')

        async def wrapped_on_rate(rate: float):
            self._run_callback('on_rate', rate)

        async def wrapped_on_volume(volume: float):
            self._run_callback('on_volume', volume)

        async def wrapped_on_shuffle(shuffle: bool):
            self._run_callback('on_shuffle', shuffle)

        async def wrapped_on_loop(status):
            self._run_callback('on_loop', status)

        async def wrapped_on_open_uri(uri: str):
            self._run_callback('on_open_uri', uri)

        async def wrapped_on_set_position(track_id: str, position: int):
            delta = self._microseconds_to_timedelta(position)
            self._run_callback('on_set_position', track_id, delta)

        async def wrapped_on_get_tracks_metadata(track_ids: list[str]):
            return await self._call_callback('on_get_tracks_metadata', track_ids)

        async def wrapped_on_add_track(uri: str, after_track: str, set_as_current: bool):
            self._run_callback('on_add_track', uri, after_track, set_as_current)

        async def wrapped_on_remove_track(track_id: str):
            self._run_callback('on_remove_track', track_id)

        async def wrapped_on_goto(track_id: str):
            self._run_callback('on_goto', track_id)

        async def wrapped_on_activate_playlist(playlist_id: str):
            self._run_callback('on_activate_playlist', playlist_id)

        # Assign wrapped callbacks
        self._interface.on_fullscreen = wrapped_on_fullscreen
        self._interface.on_raise = wrapped_on_raise
        self._interface.on_quit = wrapped_on_quit
        self._interface.on_play = wrapped_on_play
        self._interface.on_pause = wrapped_on_pause
        self._interface.on_next = wrapped_on_next
        self._interface.on_previous = wrapped_on_previous
        self._interface.on_seek = wrapped_on_seek
        self._interface.on_stop = wrapped_on_stop
        self._interface.on_play_pause = wrapped_on_play_pause
        self._interface.on_rate = wrapped_on_rate
        self._interface.on_volume = wrapped_on_volume
        self._interface.on_shuffle = wrapped_on_shuffle
        self._interface.on_loop_status = wrapped_on_loop
        self._interface.on_open_uri = wrapped_on_open_uri
        self._interface.on_set_position = wrapped_on_set_position
        self._interface.on_get_tracks_metadata = wrapped_on_get_tracks_metadata
        self._interface.on_add_track = wrapped_on_add_track
        self._interface.on_remove_track = wrapped_on_remove_track
        self._interface.on_goto = wrapped_on_goto
        self._interface.on_activate_playlist = wrapped_on_activate_playlist

    def _apply_metadata(self, metadata: dict[str, Any]) -> None:
        """Apply metadata to the playback properties."""
        metadata_bean = self._interface._playback_properties.Metadata

        field_aliases = {
            'id': 'id_',
            'id_': 'id_',
            'media_type': 'media_type',
            'duration': 'duration',
            'cover': 'cover',
            'album': 'album',
            'album_artist': 'albumArtist',
            'albumArtist': 'albumArtist',
            'artist': 'artist',
            'lyrics': 'lyrics',
            'comments': 'comments',
            'composer': 'composer',
            'genre': 'genre',
            'lyricist': 'lyricist',
            'title': 'title',
            'track_number': 'trackNumber',
            'trackNumber': 'trackNumber',
            'url': 'url',
        }

        list_fields = {'albumArtist', 'artist', 'comments', 'composer', 'genre', 'lyricist'}

        for key, value in metadata.items():
            target = field_aliases.get(key)
            if target is None:
                continue
            if target in list_fields and isinstance(value, str):
                value = [value]
            if target == 'duration' and isinstance(value, timedelta):
                value = self._timedelta_to_microseconds(value)
            setattr(metadata_bean, target, value)

        self._interface.set_playback_property(PlaybackPropertyName.Metadata, metadata_bean)

    @staticmethod
    def _timedelta_to_microseconds(td: timedelta) -> int:
        """Convert timedelta to microseconds."""
        return int(td.total_seconds() * 1_000_000)

    @staticmethod
    def _microseconds_to_timedelta(us: int) -> timedelta:
        """Convert microseconds to timedelta."""
        return timedelta(microseconds=us)

    def set_property(self, name: PropertyName, value: Any) -> None:
        self._interface.set_property(name, value)
        if name == PropertyName.Identity:
            self._identity = value

    def get_property(self, name: PropertyName) -> Any:
        return self._interface.get_property(name)

    def set_playback_property(self, name: PlaybackPropertyName, value: Any) -> None:
        self._interface.set_playback_property(name, value)

    def get_playback_property(self, name: PlaybackPropertyName) -> Any:
        return self._interface.get_playback_property(name)

    def set_tracklist_property(self, name: TrackListPropertyName, value: Any) -> None:
        self._interface.set_tracklist_property(name, value)

    def get_tracklist_property(self, name: TrackListPropertyName) -> Any:
        return self._interface.get_tracklist_property(name)

    @property
    def identity(self) -> str:
        return self.get_property(PropertyName.Identity)

    @identity.setter
    def identity(self, value: str):
        self.set_property(PropertyName.Identity, value)

    @property
    def fullscreen(self) -> bool:
        return self.get_property(PropertyName.Fullscreen)

    @fullscreen.setter
    def fullscreen(self, value: bool):
        self.set_property(PropertyName.Fullscreen, value)

    @property
    def can_quit(self) -> bool:
        return self.get_property(PropertyName.CanQuit)

    @can_quit.setter
    def can_quit(self, value: bool):
        self.set_property(PropertyName.CanQuit, value)

    @property
    def can_set_fullscreen(self) -> bool:
        return self.get_property(PropertyName.CanSetFullscreen)

    @can_set_fullscreen.setter
    def can_set_fullscreen(self, value: bool):
        self.set_property(PropertyName.CanSetFullscreen, value)

    @property
    def can_raise(self) -> bool:
        return self.get_property(PropertyName.CanRaise)

    @can_raise.setter
    def can_raise(self, value: bool):
        self.set_property(PropertyName.CanRaise, value)

    @property
    def has_tracklist(self) -> bool:
        return self.get_property(PropertyName.HasTrackList)

    @has_tracklist.setter
    def has_tracklist(self, value: bool):
        self.set_property(PropertyName.HasTrackList, value)

    @property
    def desktop_entry(self) -> str:
        return self.get_property(PropertyName.DesktopEntry)

    @desktop_entry.setter
    def desktop_entry(self, value: str):
        self.set_property(PropertyName.DesktopEntry, value)

    @property
    def supported_uri_schemes(self) -> list[str]:
        return self.get_property(PropertyName.SupportedUriSchemes)

    @supported_uri_schemes.setter
    def supported_uri_schemes(self, value: list[str]):
        self.set_property(PropertyName.SupportedUriSchemes, value)

    @property
    def supported_mime_types(self) -> list[str]:
        return self.get_property(PropertyName.SupportedMimeTypes)

    @supported_mime_types.setter
    def supported_mime_types(self, value: list[str]):
        self.set_property(PropertyName.SupportedMimeTypes, value)

    @property
    def tracks(self) -> list[str]:
        return self.get_tracklist_property(TrackListPropertyName.Tracks)

    @tracks.setter
    def tracks(self, value: list[str]):
        self.set_tracklist_property(TrackListPropertyName.Tracks, value)

    @property
    def can_edit_tracks(self) -> bool:
        return self.get_tracklist_property(TrackListPropertyName.CanEditTracks)

    @can_edit_tracks.setter
    def can_edit_tracks(self, value: bool):
        self.set_tracklist_property(TrackListPropertyName.CanEditTracks, value)

    # Metadata properties

    @property
    def title(self) -> str:
        return self._interface._playback_properties.Metadata.title

    @title.setter
    def title(self, value: str):
        self._interface._playback_properties.Metadata.title = value

    @property
    def artist(self) -> list[str]:
        return self._interface._playback_properties.Metadata.artist

    @artist.setter
    def artist(self, value: list[str] | str):
        if isinstance(value, str):
            value = [value]
        self._interface._playback_properties.Metadata.artist = value

    @property
    def album(self) -> str:
        return self._interface._playback_properties.Metadata.album

    @album.setter
    def album(self, value: str):
        self._interface._playback_properties.Metadata.album = value

    @property
    def album_artist(self) -> list[str]:
        return self._interface._playback_properties.Metadata.albumArtist

    @album_artist.setter
    def album_artist(self, value: list[str] | str):
        if isinstance(value, str):
            value = [value]
        self._interface._playback_properties.Metadata.albumArtist = value

    @property
    def cover(self) -> str:
        return self._interface._playback_properties.Metadata.cover

    @cover.setter
    def cover(self, value: str):
        self._interface._playback_properties.Metadata.cover = value

    @property
    def url(self) -> str:
        return self._interface._playback_properties.Metadata.url

    @url.setter
    def url(self, value: str):
        self._interface._playback_properties.Metadata.url = value

    @property
    def track_number(self) -> int:
        return self._interface._playback_properties.Metadata.trackNumber

    @track_number.setter
    def track_number(self, value: int):
        self._interface._playback_properties.Metadata.trackNumber = value

    @property
    def duration(self) -> timedelta | None:
        us = self._interface._playback_properties.Metadata.duration
        if us == 0:
            return None
        return self._microseconds_to_timedelta(us)

    @duration.setter
    def duration(self, value: timedelta):
        self._interface._playback_properties.Metadata.duration = self._timedelta_to_microseconds(value)

    # Playback state properties

    @property
    def position(self) -> timedelta | None:
        """Get current playback position as timedelta."""
        us = self._interface.get_playback_property(PlaybackPropertyName.Position)
        if us == 0:
            return None
        return self._microseconds_to_timedelta(us)

    @position.setter
    def position(self, value: timedelta):
        """Set playback position from timedelta."""
        self._interface.set_playback_property(
            PlaybackPropertyName.Position,
            self._timedelta_to_microseconds(value)
        )

    @property
    def is_playing(self) -> bool:
        """Read-only property. Use set_playing() to change state."""
        return self._interface.get_playback_property(PlaybackPropertyName.PlaybackStatus) == PlaybackStatus.Playing

    @property
    def is_paused(self) -> bool:
        """Read-only property. Use set_paused() to change state."""
        return self._interface.get_playback_property(PlaybackPropertyName.PlaybackStatus) == PlaybackStatus.Paused

    @property
    def is_stopped(self) -> bool:
        """Read-only property. Use set_stopped() to change state."""
        return self._interface.get_playback_property(PlaybackPropertyName.PlaybackStatus) == PlaybackStatus.Stopped

    @property
    def volume(self) -> float:
        """Get playback volume (0.0 to 1.0)."""
        return self._interface.get_playback_property(PlaybackPropertyName.Volume)

    @volume.setter
    def volume(self, value: float):
        """Set playback volume (0.0 to 1.0)."""
        self._interface.set_playback_property(PlaybackPropertyName.Volume, value)

    @property
    def shuffle(self) -> bool:
        """Get shuffle state."""
        return self._interface.get_playback_property(PlaybackPropertyName.Shuffle)

    @shuffle.setter
    def shuffle(self, value: bool):
        """Set shuffle state."""
        self._interface.set_playback_property(PlaybackPropertyName.Shuffle, value)

    @property
    def loop_status(self) -> LoopStatus:
        """Get loop status (None, Track, or Playlist)."""
        return self._interface.get_playback_property(PlaybackPropertyName.LoopStatus)

    @loop_status.setter
    def loop_status(self, value: LoopStatus):
        """Set loop status."""
        self._interface.set_playback_property(PlaybackPropertyName.LoopStatus, value)

    @property
    def rate(self) -> float:
        """Get playback rate."""
        return self._interface.get_playback_property(PlaybackPropertyName.Rate)

    @rate.setter
    def rate(self, value: float):
        """Set playback rate."""
        self._interface.set_playback_property(PlaybackPropertyName.Rate, value)

    @property
    def minimum_rate(self) -> float:
        """Get minimum playback rate."""
        return self._interface.get_playback_property(PlaybackPropertyName.MinimumRate)

    @minimum_rate.setter
    def minimum_rate(self, value: float):
        """Set minimum playback rate."""
        self._interface.set_playback_property(PlaybackPropertyName.MinimumRate, value)

    @property
    def maximum_rate(self) -> float:
        """Get maximum playback rate."""
        return self._interface.get_playback_property(PlaybackPropertyName.MaximumRate)

    @maximum_rate.setter
    def maximum_rate(self, value: float):
        """Set maximum playback rate."""
        self._interface.set_playback_property(PlaybackPropertyName.MaximumRate, value)

    # Playlist properties

    @property
    def active_playlist(self) -> PlaylistBean | None:
        """Get the currently active playlist, or None if none is active."""
        valid = self._interface._playlist_properties.ActivePlaylistValid
        if not valid:
            return None
        return self._interface._playlist_properties.ActivePlaylist

    @active_playlist.setter
    def active_playlist(self, value: PlaylistBean | None):
        """Set the active playlist."""
        if value is None:
            self._interface._playlist_properties.ActivePlaylistValid = False
        else:
            self._interface._playlist_properties.ActivePlaylistValid = True
            self._interface._playlist_properties.ActivePlaylist = value

    @property
    def playlist_count(self) -> int:
        """Get the number of available playlists."""
        return self._interface._playlist_properties.PlaylistCount

    @playlist_count.setter
    def playlist_count(self, value: int):
        """Set the number of available playlists."""
        self._interface.set_playlist_property(PlaylistPropertyName.PlaylistCount, value)

    # State convenience methods

    def set_playing(self) -> None:
        """Set playback status to Playing."""
        self._interface.set_playback_property(PlaybackPropertyName.PlaybackStatus, PlaybackStatus.Playing)

    def set_paused(self) -> None:
        """Set playback status to Paused."""
        self._interface.set_playback_property(PlaybackPropertyName.PlaybackStatus, PlaybackStatus.Paused)

    def set_stopped(self) -> None:
        """Set playback status to Stopped."""
        self._interface.set_playback_property(PlaybackPropertyName.PlaybackStatus, PlaybackStatus.Stopped)

    # Lifecycle methods

    async def start(self) -> None:
        """Start the Now Playing backend."""
        await self._interface.start()

    async def stop(self) -> None:
        """Stop the Now Playing backend."""
        await self._interface.stop()

    async def track_added(self, metadata: PlaybackProperties.MetadataBean, after_track: str) -> None:
        """Notify the backend that a track was added."""
        await self._interface.track_added(metadata, after_track)

    async def track_removed(self, track_id: str) -> None:
        """Notify the backend that a track was removed."""
        await self._interface.track_removed(track_id)

    async def track_list_replaced(self, tracks: list[str], current_track: str) -> None:
        """Notify the backend that the track list was replaced."""
        await self._interface.track_list_replaced(tracks, current_track)

    async def track_metadata_changed(self, track_id: str, metadata: PlaybackProperties.MetadataBean) -> None:
        """Notify the backend that track metadata changed."""
        await self._interface.track_metadata_changed(track_id, metadata)

    async def seeked(self, position: timedelta) -> None:
        """Notify the backend that playback was seeked."""
        await self._interface.seeked(self._timedelta_to_microseconds(position))
