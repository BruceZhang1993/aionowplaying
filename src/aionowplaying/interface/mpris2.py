import inspect
import re
from typing import Any

from dbus_fast import PropertyAccess, Variant
from dbus_fast.aio import MessageBus
from dbus_fast.service import ServiceInterface, dbus_property, method, signal

from aionowplaying.interface.base import BaseInterface, PropertyName, PlayerProperties, PlaybackProperties, \
    PlaybackPropertyName, LoopStatus, TrackListPropertyName, TrackListProperties


class DBusBeanMapper:
    NO_TRACK_PATH = "/org/mpris/MediaPlayer2/TrackList/NoTrack"
    TRACK_LIST_PATH = "/org/mpris/MediaPlayer2/TrackList"
    _OBJECT_PATH_RE = re.compile(r"^/(?:[A-Za-z0-9_]+(?:/[A-Za-z0-9_]+)*)?$")
    _TRACK_ID_SEGMENT_RE = re.compile(r"[^A-Za-z0-9_]")

    @staticmethod
    def _track_id_path(track_id: str) -> str:
        if not track_id:
            return DBusBeanMapper.NO_TRACK_PATH
        if track_id.startswith("/") and DBusBeanMapper._OBJECT_PATH_RE.fullmatch(track_id):
            return track_id

        safe = DBusBeanMapper._TRACK_ID_SEGMENT_RE.sub("_", track_id)
        if not safe:
            safe = "track"
        if safe[0].isdigit():
            safe = f"track_{safe}"
        return f"{DBusBeanMapper.TRACK_LIST_PATH}/{safe}"

    @staticmethod
    def metadata(metadata: PlaybackProperties.MetadataBean) -> dict:
        metadata_map = dict()
        metadata_map['mpris:trackid'] = Variant('o', DBusBeanMapper._track_id_path(metadata.id_))
        metadata_map['mpris:length'] = Variant('x', metadata.duration)
        metadata_map['mpris:artUrl'] = Variant('s', metadata.cover)
        metadata_map['xesam:album'] = Variant('s', metadata.album)
        metadata_map['xesam:albumArtist'] = Variant('as', metadata.albumArtist)
        metadata_map['xesam:artist'] = Variant('as', metadata.artist)
        metadata_map['xesam:asText'] = Variant('s', metadata.lyrics)
        metadata_map['xesam:comment'] = Variant('as', metadata.comments)
        metadata_map['xesam:composer'] = Variant('as', metadata.composer)
        metadata_map['xesam:genre'] = Variant('as', metadata.genre)
        metadata_map['xesam:lyricist'] = Variant('as', metadata.lyricist)
        metadata_map['xesam:title'] = Variant('s', metadata.title)
        metadata_map['xesam:trackNumber'] = Variant('i', metadata.trackNumber)
        metadata_map['xesam:url'] = Variant('s', metadata.url)
        return metadata_map


class MprisPlayerServiceInterface(ServiceInterface):
    def __init__(self, bus_name: str, it: 'Mpris2Interface' = None):
        super().__init__(bus_name)
        self._properties = PlaybackProperties()
        self._it = it

    def set_property(self, name: str, value: Any):
        setattr(self._properties, name, value)
        if name == PlaybackPropertyName.Position:
            return
        if isinstance(value, PlaybackProperties.MetadataBean):
            value = DBusBeanMapper.metadata(value)
        self.emit_properties_changed({name: value})

    @dbus_property(access=PropertyAccess.READ, name=PlaybackPropertyName.PlaybackStatus.value)
    def playback_status(self) -> 's':
        return self._properties.PlaybackStatus.value

    @dbus_property(access=PropertyAccess.READWRITE, name=PlaybackPropertyName.LoopStatus.value)
    def loop_status(self) -> 's':
        return self._properties.LoopStatus.value

    @loop_status.setter
    async def loop_status(self, value: 's'):
        if self._properties.CanControl:
            await self._it.on_loop_status(LoopStatus(value))
            self._properties.LoopStatus = LoopStatus(value)

    @dbus_property(access=PropertyAccess.READWRITE, name=PlaybackPropertyName.Rate.value)
    def rate(self) -> 'd':
        return self._properties.Rate

    @rate.setter
    async def rate(self, value: 'd'):
        await self._it.on_rate(value)
        self._properties.Rate = value

    @dbus_property(access=PropertyAccess.READWRITE, name=PlaybackPropertyName.Shuffle.value)
    def shuffle(self) -> 'b':
        return self._properties.Shuffle

    @shuffle.setter
    async def shuffle(self, value: 'b'):
        if self._properties.CanControl:
            await self._it.on_shuffle(value)
            self._properties.Shuffle = value

    @dbus_property(access=PropertyAccess.READ, name=PlaybackPropertyName.Metadata.value)
    def metadata(self) -> 'a{sv}':
        metadata = self._properties.Metadata
        return DBusBeanMapper.metadata(metadata)

    @dbus_property(access=PropertyAccess.READWRITE, name=PlaybackPropertyName.Volume.value)
    def volume(self) -> 'd':
        return self._properties.Volume

    @volume.setter
    async def volume(self, value: 'd'):
        if self._properties.CanControl:
            await self._it.on_volume(value)
            self._properties.Volume = value

    @dbus_property(access=PropertyAccess.READ, name=PlaybackPropertyName.Position.value)
    def position(self) -> 'x':
        return self._properties.Position

    @dbus_property(access=PropertyAccess.READ, name=PlaybackPropertyName.MinimumRate.value)
    def minimum_rate(self) -> 'd':
        return self._properties.MinimumRate

    @dbus_property(access=PropertyAccess.READ, name=PlaybackPropertyName.MaximumRate.value)
    def maximum_rate(self) -> 'd':
        return self._properties.MaximumRate

    @dbus_property(access=PropertyAccess.READ, name=PlaybackPropertyName.CanGoNext.value)
    def can_go_next(self) -> 'b':
        return self._properties.CanGoNext

    @dbus_property(access=PropertyAccess.READ, name=PlaybackPropertyName.CanGoPrevious.value)
    def can_go_previous(self) -> 'b':
        return self._properties.CanGoPrevious

    @dbus_property(access=PropertyAccess.READ, name=PlaybackPropertyName.CanPlay.value)
    def can_play(self) -> 'b':
        return self._properties.CanPlay

    @dbus_property(access=PropertyAccess.READ, name=PlaybackPropertyName.CanPause.value)
    def can_pause(self) -> 'b':
        return self._properties.CanPause

    @dbus_property(access=PropertyAccess.READ, name=PlaybackPropertyName.CanSeek.value)
    def can_seek(self) -> 'b':
        return self._properties.CanSeek

    @dbus_property(access=PropertyAccess.READ, name=PlaybackPropertyName.CanControl.value)
    def can_control(self) -> 'b':
        return self._properties.CanControl

    @signal(name='Seeked')
    async def seeked(self, position: int) -> 'x':
        return position

    @method(name="Next")
    async def next(self):
        if self._properties.CanGoNext:
            await self._it.on_next()

    @method(name="Previous")
    async def previous(self):
        if self._properties.CanGoPrevious:
            await self._it.on_previous()

    @method(name="Pause")
    async def pause(self):
        if self._properties.CanPause:
            await self._it.on_pause()

    @method(name="PlayPause")
    async def play_pause(self):
        if self._properties.CanPause:
            await self._it.on_play_pause()

    @method(name="Stop")
    async def stop(self):
        if self._properties.CanControl:
            await self._it.on_stop()

    @method(name="Play")
    async def play(self):
        if self._properties.CanPlay:
            await self._it.on_play()

    @method(name="Seek")
    async def seek(self, offset: 'x'):
        if self._properties.CanSeek:
            await self._it.on_seek(offset)

    @method(name="OpenUri")
    async def open_uri(self, uri: 's'):
        await self._it.on_open_uri(uri)

    @method(name="SetPosition")
    async def set_position(self, track_id: 'o', position: 'x'):
        if self._properties.CanSeek:
            await self._it.on_set_position(track_id, position)

    def get_property(self, key):
        return getattr(self._properties, key)


class MprisServiceInterface(ServiceInterface):
    def __init__(self, bus_name: str, it: 'Mpris2Interface' = None):
        super().__init__(bus_name)
        self._properties = PlayerProperties()
        self._it = it

    @dbus_property(access=PropertyAccess.READWRITE, name=PropertyName.Fullscreen.value)
    def fullscreen(self) -> 'b':
        return self._properties.Fullscreen

    @fullscreen.setter
    async def fullscreen(self, value: 'b'):
        if self._properties.CanSetFullscreen:
            await self._it.on_fullscreen(value)
            self._properties.Fullscreen = value

    @dbus_property(access=PropertyAccess.READ, name=PropertyName.CanQuit.value)
    def can_quit(self) -> 'b':
        return self._properties.CanQuit

    @dbus_property(access=PropertyAccess.READ, name=PropertyName.CanSetFullscreen.value)
    def can_set_fullscreen(self) -> 'b':
        return self._properties.CanSetFullscreen

    @dbus_property(access=PropertyAccess.READ, name=PropertyName.HasTrackList.value)
    def has_track_list(self) -> 'b':
        return self._properties.HasTrackList

    @dbus_property(access=PropertyAccess.READ, name=PropertyName.CanRaise.value)
    def can_raise(self) -> 'b':
        return self._properties.CanRaise

    @dbus_property(access=PropertyAccess.READ, name=PropertyName.Identity.value)
    def identity(self) -> 's':
        return self._properties.Identity

    @dbus_property(access=PropertyAccess.READ, name=PropertyName.DesktopEntry.value)
    def desktop_entry(self) -> 's':
        return self._properties.DesktopEntry

    @dbus_property(access=PropertyAccess.READ, name=PropertyName.SupportedUriSchemes.value)
    def supported_uri_schemes(self) -> 'as':
        return self._properties.SupportedUriSchemes

    @dbus_property(access=PropertyAccess.READ, name=PropertyName.SupportedMimeTypes.value)
    def supported_mime_types(self) -> 'as':
        return self._properties.SupportedMimeTypes

    @method(name='Raise')
    async def raise_(self):
        if self._properties.CanRaise:
            await self._it.on_raise()

    @method(name='Quit')
    async def quit(self):
        if self._properties.CanQuit:
            await self._it.on_quit()

    def set_property(self, name: str, value: Any):
        setattr(self._properties, name, value)
        self.emit_properties_changed({name: value})

    def get_property(self, key):
        return getattr(self._properties, key)


class MprisTracklistServiceInterface(ServiceInterface):
    def __init__(self, bus_name: str, it: 'Mpris2Interface' = None):
        super().__init__(bus_name)
        self._properties = TrackListProperties()
        self._it = it

    def set_property(self, name: str, value: Any):
        if name == TrackListPropertyName.Tracks.value:
            value = [DBusBeanMapper._track_id_path(track_id) for track_id in value]
        setattr(self._properties, name, value)
        if name == TrackListPropertyName.Tracks.value:
            self.emit_properties_changed({}, [name])
        else:
            self.emit_properties_changed({name: value})

    @dbus_property(access=PropertyAccess.READ, name=TrackListPropertyName.CanEditTracks.value)
    def can_edit_tracks(self) -> 'b':
        return self._properties.CanEditTracks

    @dbus_property(access=PropertyAccess.READ, name=TrackListPropertyName.Tracks.value)
    def tracks(self) -> 'ao':
        return self._properties.Tracks

    @signal(name="TrackAdded")
    def track_added(self, metadata: dict, after_track: str) -> "a{sv}o":
        return metadata, after_track

    @signal(name="TrackRemoved")
    def track_removed(self, track_id: str) -> "o":
        return track_id

    @signal(name="TrackListReplaced")
    def track_list_replaced(self, tracks: list[str], current_track: str) -> "aoo":
        return tracks, current_track

    @signal(name="TrackMetadataChanged")
    def track_metadata_changed(self, track_id: str, metadata: dict) -> "oa{sv}":
        return track_id, metadata

    @method(name="GetTracksMetadata")
    async def get_tracks_metadata(self, track_ids: 'ao') -> 'aa{sv}':
        items = await self._it.on_get_tracks_metadata(list(track_ids))
        return [DBusBeanMapper.metadata(item) for item in items]

    @method(name="AddTrack")
    async def add_track(self, uri: 's', after_track: 'o', set_as_current: 'b'):
        if self._properties.CanEditTracks:
            await self._it.on_add_track(uri, after_track, set_as_current)

    @method(name="RemoveTrack")
    async def remove_track(self, track_id: 'o'):
        if self._properties.CanEditTracks:
            await self._it.on_remove_track(track_id)

    @method(name="GoTo")
    async def go_to(self, track_id: 'o'):
        await self._it.on_goto(track_id)

    def get_property(self, key):
        return getattr(self._properties, key)


class Mpris2Interface(BaseInterface):
    def __init__(self, name: str):
        super().__init__(name)
        self.dbus = None
        self._bus_name = f'org.mpris.MediaPlayer2.{name}'
        self._entry_name = 'org.mpris.MediaPlayer2'
        self._player_entry_name = 'org.mpris.MediaPlayer2.Player'
        self._player_tracklist_name = 'org.mpris.MediaPlayer2.TrackList'
        self._object_path = '/org/mpris/MediaPlayer2'
        self._bus = MprisServiceInterface(self._entry_name, it=self)
        self._bus._properties.HasTrackList = True
        self._player_bus = MprisPlayerServiceInterface(self._player_entry_name, it=self)
        self._tracklist_bus = MprisTracklistServiceInterface(self._player_tracklist_name, it=self)

    def set_property(self, name: PropertyName, value: Any):
        self._bus.set_property(name.value, value)

    def set_playback_property(self, name: PlaybackPropertyName, value: Any):
        self._player_bus.set_property(name.value, value)

    def set_tracklist_property(self, name: TrackListPropertyName, value: Any):
        self._tracklist_bus.set_property(name.value, value)

    def get_property(self, name: PropertyName) -> Any:
        return self._bus.get_property(name.value)

    def get_playback_property(self, name: PlaybackPropertyName) -> Any:
        return self._player_bus.get_property(name.value)

    def get_tracklist_property(self, name: TrackListPropertyName) -> Any:
        return self._tracklist_bus.get_property(name.value)

    async def seeked(self, position: int):
        await self._player_bus.seeked(position)

    async def _maybe_await(self, value):
        if inspect.isawaitable(value):
            return await value
        return value

    async def track_added(self, metadata, after_track):
        result = self._tracklist_bus.track_added(
            DBusBeanMapper.metadata(metadata),
            DBusBeanMapper._track_id_path(after_track),
        )
        return await self._maybe_await(result)

    async def track_removed(self, track_id):
        result = self._tracklist_bus.track_removed(DBusBeanMapper._track_id_path(track_id))
        return await self._maybe_await(result)

    async def track_list_replaced(self, tracks, current_track):
        result = self._tracklist_bus.track_list_replaced(
            [DBusBeanMapper._track_id_path(track_id) for track_id in tracks],
            DBusBeanMapper._track_id_path(current_track),
        )
        return await self._maybe_await(result)

    async def track_metadata_changed(self, track_id, metadata):
        result = self._tracklist_bus.track_metadata_changed(
            DBusBeanMapper._track_id_path(track_id),
            DBusBeanMapper.metadata(metadata),
        )
        return await self._maybe_await(result)

    async def start(self):
        self.dbus = await MessageBus().connect()
        self.dbus.export(self._object_path, self._bus)
        self.dbus.export(self._object_path, self._player_bus)
        self.dbus.export(self._object_path, self._tracklist_bus)
        await self.dbus.request_name(self._bus_name)
        await self.dbus.wait_for_disconnect()

    async def stop(self):
        if self.dbus is None:
            return
        self.dbus.disconnect()
