import asyncio
from typing import Any

from winrt.windows.foundation import Uri
from winrt.windows.media import SystemMediaTransportControlsTimelineProperties, SystemMediaTransportControls, \
    SystemMediaTransportControlsDisplayUpdater, MediaPlaybackStatus, MediaPlaybackType, MediaPlaybackAutoRepeatMode, \
    AutoRepeatModeChangeRequestedEventArgs, SystemMediaTransportControlsButtonPressedEventArgs, \
    SystemMediaTransportControlsButton
from winrt.windows.media.playback import MediaPlayer
from winrt.windows.storage.streams import RandomAccessStreamReference

from aionowplaying import BaseInterface, PropertyName, PlaybackPropertyName
from aionowplaying.interface.base import TrackListPropertyName, PlaybackStatus, PlaybackProperties, LoopStatus


class WindowsInterface(BaseInterface):
    def __init__(self, name):
        super(WindowsInterface, self).__init__(name)
        self._playback_properties = PlaybackProperties()
        self._player = MediaPlayer()
        self._controls: SystemMediaTransportControls = self._player.system_media_transport_controls
        self._updater: SystemMediaTransportControlsDisplayUpdater = self._controls.display_updater
        self._timeline = SystemMediaTransportControlsTimelineProperties()
        self._controls.add_auto_repeat_mode_change_requested(self.auto_repeat_mode_change_requested)
        self._controls.add_button_pressed(self.button_pressed)

    def button_pressed(self, _, args: SystemMediaTransportControlsButtonPressedEventArgs):
        button: SystemMediaTransportControlsButton = args.button
        if button == SystemMediaTransportControlsButton.PLAY and self._playback_properties.CanPlay:
            asyncio.run(self.on_play())
            self._controls.playback_status = MediaPlaybackStatus.PLAYING
            self._playback_properties.PlaybackStatus = PlaybackStatus.Playing
        if button == SystemMediaTransportControlsButton.PAUSE and self._playback_properties.CanPause:
            asyncio.run(self.on_pause())
            self._controls.playback_status = MediaPlaybackStatus.PAUSED
            self._playback_properties.PlaybackStatus = PlaybackStatus.Paused
        if button == SystemMediaTransportControlsButton.NEXT and self._playback_properties.CanGoNext:
            asyncio.run(self.on_next())
        if button == SystemMediaTransportControlsButton.PREVIOUS and self._playback_properties.CanGoPrevious:
            asyncio.run(self.on_previous())

    def auto_repeat_mode_change_requested(self, _, args: AutoRepeatModeChangeRequestedEventArgs):
        value = LoopStatus.None_
        mode: MediaPlaybackAutoRepeatMode = args.requested_auto_repeat_mode
        if mode == MediaPlaybackAutoRepeatMode.LIST:
            value = LoopStatus.Playlist
        elif mode == MediaPlaybackAutoRepeatMode.TRACK:
            value = LoopStatus.Track
        asyncio.run(self.on_loop_status(value))
        self._playback_properties.LoopStatus = value

    def set_property(self, name: PropertyName, value: Any):
        pass

    def set_playback_property(self, name: PlaybackPropertyName, value: Any):
        if name == PlaybackPropertyName.CanPlay:
            self._controls.is_play_enabled = value
            self._playback_properties.CanPlay = value
        elif name == PlaybackPropertyName.CanPause:
            self._controls.is_pause_enabled = value
            self._playback_properties.CanPause = value
        elif name == PlaybackPropertyName.CanGoNext:
            self._controls.is_next_enabled = value
            self._playback_properties.CanGoNext = value
        elif name == PlaybackPropertyName.CanGoPrevious:
            self._controls.is_previous_enabled = value
            self._playback_properties.CanGoPrevious = value
        elif name == PlaybackPropertyName.PlaybackStatus:
            if value == PlaybackStatus.Playing:
                self._controls.playback_status = MediaPlaybackStatus.PLAYING
            elif value == PlaybackStatus.Paused:
                self._controls.playback_status = MediaPlaybackStatus.PAUSED
            elif value == PlaybackStatus.Stopped:
                self._controls.playback_status = MediaPlaybackStatus.STOPPED
            self._playback_properties.PlaybackStatus = value
        elif name == PlaybackPropertyName.Metadata:
            self._update_metadata(value)
            self._playback_properties.Metadata = value
        elif name == PlaybackPropertyName.Shuffle:
            self._controls.is_shuffle_enabled = value
            self._playback_properties.Shuffle = value
        elif name == PlaybackPropertyName.Rate:
            self._controls.playback_rate = value
            self._playback_properties.Rate = value
        elif name == PlaybackPropertyName.LoopStatus:
            if value == LoopStatus.None_:
                self._controls.auto_repeat_mode = MediaPlaybackAutoRepeatMode.NONE
            elif value == LoopStatus.Playlist:
                self._controls.auto_repeat_mode = MediaPlaybackAutoRepeatMode.LIST
            elif value == LoopStatus.Track:
                self._controls.auto_repeat_mode = MediaPlaybackAutoRepeatMode.TRACK
            self._playback_properties.LoopStatus = value

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
