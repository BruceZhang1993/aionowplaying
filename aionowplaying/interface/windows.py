import asyncio
from typing import Any

from winrt.windows.foundation import Uri
from winrt.windows.media import SystemMediaTransportControlsTimelineProperties, SystemMediaTransportControls, \
    SystemMediaTransportControlsDisplayUpdater, MediaPlaybackStatus, MediaPlaybackType
from winrt.windows.media.playback import MediaPlayer
from winrt.windows.storage.streams import RandomAccessStreamReference

from aionowplaying import BaseInterface, PropertyName, PlaybackPropertyName
from aionowplaying.interface.base import TrackListPropertyName, PlaybackStatus, PlaybackProperties


class WindowsInterface(BaseInterface):
    def __init__(self, name):
        super(WindowsInterface, self).__init__(name)
        self._player = MediaPlayer()
        self._controls: SystemMediaTransportControls = self._player.system_media_transport_controls
        self._updater: SystemMediaTransportControlsDisplayUpdater = self._controls.display_updater
        self._timeline = SystemMediaTransportControlsTimelineProperties()

    def set_property(self, name: PropertyName, value: Any):
        pass

    def set_playback_property(self, name: PlaybackPropertyName, value: Any):
        if name == PlaybackPropertyName.CanPlay:
            self._controls.is_play_enabled = value
        elif name == PlaybackPropertyName.CanPause:
            self._controls.is_pause_enabled = value
        elif name == PlaybackPropertyName.CanGoNext:
            self._controls.is_next_enabled = value
        elif name == PlaybackPropertyName.CanGoPrevious:
            self._controls.is_previous_enabled = value
        elif name == PlaybackPropertyName.PlaybackStatus:
            if value == PlaybackStatus.Playing:
                self._controls.playback_status = MediaPlaybackStatus.PLAYING
            elif value == PlaybackStatus.Paused:
                self._controls.playback_status = MediaPlaybackStatus.PAUSED
            elif value == PlaybackStatus.Stopped:
                self._controls.playback_status = MediaPlaybackStatus.STOPPED
        elif name == PlaybackPropertyName.Metadata:
            self._update_metadata(value)

    def _update_metadata(self, value: PlaybackProperties.MetadataBean):
        self._updater.type = MediaPlaybackType.MUSIC
        self._updater.music_properties.artist = ','.join(value.artist)
        self._updater.music_properties.title = value.title
        self._updater.music_properties.album_title = value.album
        self._updater.thumbnail = RandomAccessStreamReference.create_from_uri(Uri(value.url))
        self._updater.update()

    def set_tracklist_property(self, name: TrackListPropertyName, value: Any):
        pass

    async def start(self):
        while True:
            await asyncio.sleep(1)
