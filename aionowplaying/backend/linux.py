from typing import List, Optional

from dbus_next import PropertyAccess, Variant
from dbus_next.glib import MessageBus
from dbus_next.service import ServiceInterface, dbus_property, method, signal

from aionowplaying.backend.base import BaseNowPlayingBackend
from aionowplaying.enum import LoopStatus
from aionowplaying.interface import MPInterface, MPPlayerInterface, MPTrackListInterface
from aionowplaying.interface_old.base import PropertyName, PlaybackPropertyName, PlaybackProperties, \
    TrackListPropertyName
from aionowplaying.model import Metadata


class DBusBeanMapper:
    @staticmethod
    def metadata(metadata: Metadata) -> dict:
        metadata_map = dict()
        metadata_map['mpris:trackid'] = Variant('s', metadata.trackId)
        metadata_map['mpris:length'] = Variant('x', metadata.length)
        metadata_map['mpris:artUrl'] = Variant('s', metadata.artUrl)
        metadata_map['xesam:album'] = Variant('s', metadata.album)
        metadata_map['xesam:albumArtist'] = Variant('as', metadata.albumArtist)
        metadata_map['xesam:artist'] = Variant('as', metadata.artist)
        metadata_map['xesam:asText'] = Variant('s', metadata.asText)
        metadata_map['xesam:comment'] = Variant('as', metadata.comment)
        metadata_map['xesam:composer'] = Variant('as', metadata.composer)
        metadata_map['xesam:genre'] = Variant('as', metadata.genre)
        metadata_map['xesam:lyricist'] = Variant('as', metadata.lyricist)
        metadata_map['xesam:title'] = Variant('s', metadata.title)
        metadata_map['xesam:trackNumber'] = Variant('i', metadata.trackNumber)
        metadata_map['xesam:url'] = Variant('s', metadata.url)
        return metadata_map


class MprisServiceInterface(ServiceInterface):
    def __init__(self, bus_name: str, it: MPInterface = None):
        super().__init__(bus_name)
        self._it = it

    @dbus_property(access=PropertyAccess.READWRITE, name=PropertyName.Fullscreen.value)
    def fullscreen(self) -> 'b':
        return self._it.fullscreen

    @fullscreen.setter
    def fullscreen(self, value: 'b'):
        self._it.fullscreen = value

    @dbus_property(access=PropertyAccess.READ, name=PropertyName.CanQuit.value)
    def can_quit(self) -> 'b':
        return self._it.canQuit

    @dbus_property(access=PropertyAccess.READ, name=PropertyName.CanSetFullscreen.value)
    def can_set_fullscreen(self) -> 'b':
        return self._it.canSetFullscreen

    @dbus_property(access=PropertyAccess.READ, name=PropertyName.HasTrackList.value)
    def has_track_list(self) -> 'b':
        return self._it.hasTrackList

    @dbus_property(access=PropertyAccess.READ, name=PropertyName.CanRaise.value)
    def can_raise(self) -> 'b':
        return self._it.canRaise

    @dbus_property(access=PropertyAccess.READ, name=PropertyName.Identity.value)
    def identity(self) -> 's':
        return self._it.identity

    @dbus_property(access=PropertyAccess.READ, name=PropertyName.DesktopEntry.value)
    def desktop_entry(self) -> 's':
        return self._it.desktopEntry

    @dbus_property(access=PropertyAccess.READ, name=PropertyName.SupportedUriSchemes.value)
    def supported_uri_schemes(self) -> 'as':
        return self._it.supportedUriSchemes

    @dbus_property(access=PropertyAccess.READ, name=PropertyName.SupportedMimeTypes.value)
    def supported_mime_types(self) -> 'as':
        return self._it.supportedMimeTypes

    @method(name='Raise')
    def raise_(self):
        if self._it.canRaise:
            self._it.raise_()

    @method(name='Quit')
    def quit(self):
        if self._it.canQuit:
            self._it.quit()


class MprisPlayerServiceInterface(ServiceInterface):
    def __init__(self, bus_name: str, it: MPPlayerInterface = None):
        super().__init__(bus_name)
        self._it = it

    @dbus_property(access=PropertyAccess.READ, name=PlaybackPropertyName.PlaybackStatus.value)
    def playback_status(self) -> 's':
        return self._it.playbackStatus.value

    @dbus_property(access=PropertyAccess.READWRITE, name=PlaybackPropertyName.LoopStatus.value)
    def loop_status(self) -> 's':
        return self._it.loopStatus.value

    @loop_status.setter
    def loop_status(self, value: 's'):
        if self._it.canControl:
            self._it.loopStatus = LoopStatus(value)

    @dbus_property(access=PropertyAccess.READWRITE, name=PlaybackPropertyName.Rate.value)
    def rate(self) -> 'd':
        return self._it.rate

    @rate.setter
    def rate(self, value: 'd'):
        self._it.rate = value

    @dbus_property(access=PropertyAccess.READWRITE, name=PlaybackPropertyName.Shuffle.value)
    def shuffle(self) -> 'b':
        return self._it.shuffle

    @shuffle.setter
    def shuffle(self, value: 'b'):
        if self._it.canControl:
            self._it.shuffle = value

    @dbus_property(access=PropertyAccess.READ, name=PlaybackPropertyName.Metadata.value)
    def metadata(self) -> 'a{sv}':
        metadata = self._it.metadata
        return DBusBeanMapper.metadata(metadata)

    @dbus_property(access=PropertyAccess.READWRITE, name=PlaybackPropertyName.Volume.value)
    def volume(self) -> 'd':
        return self._it.volume

    @volume.setter
    def volume(self, value: 'd'):
        if self._it.canControl:
            self._it.volume = value

    @dbus_property(access=PropertyAccess.READ, name=PlaybackPropertyName.Position.value)
    def position(self) -> 'x':
        return self._it.position

    @dbus_property(access=PropertyAccess.READ, name=PlaybackPropertyName.MinimumRate.value)
    def minimum_rate(self) -> 'd':
        return self._it.minimumRate

    @dbus_property(access=PropertyAccess.READ, name=PlaybackPropertyName.MaximumRate.value)
    def maximum_rate(self) -> 'd':
        return self._it.maximumRate

    @dbus_property(access=PropertyAccess.READ, name=PlaybackPropertyName.CanGoNext.value)
    def can_go_next(self) -> 'b':
        return self._it.canGoNext

    @dbus_property(access=PropertyAccess.READ, name=PlaybackPropertyName.CanGoPrevious.value)
    def can_go_previous(self) -> 'b':
        return self._it.canGoPrevious

    @dbus_property(access=PropertyAccess.READ, name=PlaybackPropertyName.CanPlay.value)
    def can_play(self) -> 'b':
        return self._it.canPlay

    @dbus_property(access=PropertyAccess.READ, name=PlaybackPropertyName.CanPause.value)
    def can_pause(self) -> 'b':
        return self._it.canPause

    @dbus_property(access=PropertyAccess.READ, name=PlaybackPropertyName.CanSeek.value)
    def can_seek(self) -> 'b':
        return self._it.canSeek

    @dbus_property(access=PropertyAccess.READ, name=PlaybackPropertyName.CanControl.value)
    def can_control(self) -> 'b':
        return self._it.canControl

    @signal(name='Seeked')
    def seeked(self, position: 'x'):
        pass

    @method(name="Next")
    def next(self):
        if self._it.canGoNext:
            self._it.next()

    @method(name="Previous")
    def previous(self):
        if self._it.canGoPrevious:
            self._it.previous()

    @method(name="Pause")
    def pause(self):
        if self._it.canPause:
            self._it.pause()

    @method(name="PlayPause")
    def play_pause(self):
        if self._it.canPause:
            self._it.playPause()

    @method(name="Stop")
    def stop(self):
        if self._it.canControl:
            self._it.stop()

    @method(name="Play")
    def play(self):
        if self._it.canPlay:
            self._it.play()

    @method(name="Seek")
    def seek(self, offset: 'x'):
        if self._it.canSeek:
            self._it.seek(offset)

    @method(name="OpenUri")
    def open_uri(self, uri: 's'):
        self._it.openUri(uri)

    @method(name="SetPosition")
    def set_position(self, track_id: 'o', position: 'x'):
        if self._it.canSeek:
            self._it.setPosition(track_id, position)


class MprisTracklistServiceInterface(ServiceInterface):
    def __init__(self, bus_name: str, it: MPTrackListInterface = None):
        super().__init__(bus_name)
        self._it = it

    @dbus_property(access=PropertyAccess.READ, name=TrackListPropertyName.CanEditTracks.value)
    def can_edit_tracks(self) -> 'b':
        return self._it.canEditTracks

    @dbus_property(access=PropertyAccess.READ, name=TrackListPropertyName.Tracks.value)
    def tracks(self) -> 'ao':
        return self._it.tracks

    @method(name="GetTracksMetadata")
    def get_tracks_metadata(self, track_ids: 'ao') -> 'aa{sv}':
        return self._it.getTracksMetadata(track_ids)

    @method(name="AddTrack")
    def add_track(self, uri: 's', after_track_id: 'o', set_as_current: 'b'):
        self._it.addTrack(uri, after_track_id, set_as_current)

    @method(name="RemoveTrack")
    def remove_track(self, track_id: 'o'):
        self._it.removeTrack(track_id)

    @method(name="GoTo")
    def goto(self, track_id: 'o'):
        self._it.goTo(track_id)

    @signal(name="TrackListReplaced")
    def track_list_replaced(self, track_ids: 'ao', current_track_id: 'o'):
        pass

    @signal(name="TrackAdded")
    def track_added(self, metadata: 'a{sv}', after_track_id: 'o'):
        pass

    @signal(name="TrackRemoved")
    def track_removed(self, track_id: 'o'):
        pass

    @signal(name="TrackMetadataChanged")
    def track_metadata_changed(self, track_id: 'o', metadata: 'a{sv}'):
        pass


class LinuxNowPlayingBackend(BaseNowPlayingBackend):
    @staticmethod
    def target_platforms() -> List[str]:
        return ['linux']

    def __init__(self, interface: MPInterface, player_interface: MPPlayerInterface,
                 tracklist_interface: MPTrackListInterface):
        super().__init__(interface, player_interface, tracklist_interface)
        self._dbus: Optional[MessageBus] = None
        self._bus_name = f'org.mpris.MediaPlayer2.{interface.id}'
        self._entry_name = 'org.mpris.MediaPlayer2'
        self._player_entry_name = 'org.mpris.MediaPlayer2.Player'
        self._player_tracklist_name = 'org.mpris.MediaPlayer2.TrackList'
        self._object_path = '/org/mpris/MediaPlayer2'
        self._bus = MprisServiceInterface(self._entry_name, interface)
        self._player_bus = MprisPlayerServiceInterface(self._player_entry_name, player_interface)
        self._tracklist_bus = MprisTracklistServiceInterface(self._player_tracklist_name, tracklist_interface)

    def seeked(self, position: int):
        self._player_bus.seeked(position)

    def tracklist_replaced(self, tracks: List[str], current: str):
        self._tracklist_bus.track_list_replaced(tracks, current)

    def track_added(self, metadata: Metadata, after_track: str):
        self._tracklist_bus.track_added(DBusBeanMapper.metadata(metadata), after_track)

    def track_removed(self, track: str):
        self._tracklist_bus.track_removed(track)

    def track_metadata_changed(self, track: str, metadata: Metadata):
        self._tracklist_bus.track_metadata_changed(track, DBusBeanMapper.metadata(metadata))

    def run(self):
        self._dbus = MessageBus()
        self._dbus.connect()
        self._dbus.export(self._object_path, self._bus)
        self._dbus.export(self._object_path, self._player_bus)
        self._dbus.request_name(self._bus_name)

    def destroy(self):
        if self._dbus is None:
            return
        self._dbus.disconnect()
