from typing import Any

from dbus_next import PropertyAccess, Variant
from dbus_next.aio import MessageBus
from dbus_next.service import ServiceInterface, dbus_property, method, signal

from aionowplaying.interface.base import BaseInterface, PropertyName, PlayerProperties, PlaybackProperties, \
    PlaybackPropertyName, LoopStatus, TrackListPropertyName, TrackListProperties


class DBusBeanMapper:
    @staticmethod
    def metadata(metadata: PlaybackProperties.MetadataBean) -> dict:
        metadata_map = dict()
        metadata_map['mpris:trackid'] = Variant('s', metadata.id_)
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
        setattr(self._properties, name, value)

    @dbus_property(access=PropertyAccess.READ, name=TrackListPropertyName.CanEditTracks.value)
    def can_edit_tracks(self) -> 'b':
        return self._properties.CanEditTracks

    @dbus_property(access=PropertyAccess.READ, name=TrackListPropertyName.Tracks.value)
    def tracks(self) -> 'ao':
        return self._properties.Tracks

    def get_property(self, key):
        return getattr(self._properties, key)


class Mpris2Interface(BaseInterface):
    def __init__(self, name: str):
        super().__init__(name)
        self._bus_name = f'org.mpris.MediaPlayer2.{name}'
        self._entry_name = 'org.mpris.MediaPlayer2'
        self._player_entry_name = 'org.mpris.MediaPlayer2.Player'
        self._player_tracklist_name = 'org.mpris.MediaPlayer2.TrackList'
        self._object_path = '/org/mpris/MediaPlayer2'
        self._bus = MprisServiceInterface(self._entry_name, it=self)
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

    async def start(self):
        bus = await MessageBus().connect()
        bus.export(self._object_path, self._bus)
        bus.export(self._object_path, self._player_bus)
        await bus.request_name(self._bus_name)
        await bus.wait_for_disconnect()


if __name__ == '__main__':
    import asyncio

    mp = Mpris2Interface('aionowplaying')
    mp.set_property(PropertyName.CanQuit, True)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(mp.start())
