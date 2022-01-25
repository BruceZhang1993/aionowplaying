import asyncio
from typing import Any

from winrt.windows.foundation import Uri, TimeSpan
from winrt.windows.media import SystemMediaTransportControlsTimelineProperties, SystemMediaTransportControls, \
    SystemMediaTransportControlsDisplayUpdater, MediaPlaybackStatus, MediaPlaybackType, MediaPlaybackAutoRepeatMode, \
    AutoRepeatModeChangeRequestedEventArgs, SystemMediaTransportControlsButtonPressedEventArgs, \
    SystemMediaTransportControlsButton, PlaybackPositionChangeRequestedEventArgs, PlaybackRateChangeRequestedEventArgs, \
    SystemMediaTransportControlsPropertyChangedEventArgs, SystemMediaTransportControlsProperty, \
    ShuffleEnabledChangeRequestedEventArgs
from winrt.windows.media.playback import MediaPlayer
from winrt.windows.storage.streams import RandomAccessStreamReference

from aionowplaying import BaseInterface, PropertyName, PlaybackPropertyName
from aionowplaying.interface.base import TrackListPropertyName, PlaybackStatus, PlaybackProperties, LoopStatus, \
    MediaType


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
        self._controls.add_playback_position_change_requested(self.playback_position_change_requested)
        self._controls.add_playback_rate_change_requested(self.playback_rate_change_requested)
        self._controls.add_property_changed(self.property_changed)
        self._controls.add_shuffle_enabled_change_requested(self.shuffle_change_requested)

    def shuffle_change_requested(self, _, args: ShuffleEnabledChangeRequestedEventArgs):
        shuffle_enabled: bool = args.requested_shuffle_enabled
        asyncio.run(self.on_shuffle(shuffle_enabled))

    def property_changed(self, _, args: SystemMediaTransportControlsPropertyChangedEventArgs):
        property_: SystemMediaTransportControlsProperty = args.property
        if property_ == SystemMediaTransportControlsProperty.SOUND_LEVEL:
            asyncio.run(self.on_volume(self._controls.sound_level))

    def playback_rate_change_requested(self, _, args: PlaybackRateChangeRequestedEventArgs):
        rate: float = args.requested_playback_rate
        asyncio.run(self.on_rate(rate))

    def playback_position_change_requested(self, _, args: PlaybackPositionChangeRequestedEventArgs):
        position: TimeSpan = args.requested_playback_position
        print(position, dir(position))
        if self._playback_properties.CanSeek:
            asyncio.run(self.on_set_position(self._playback_properties.Metadata.id_, position.duration))

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
        elif name == PlaybackPropertyName.Position:
            self._timeline.position = TimeSpan(value)
            self._controls.update_timeline_properties(self._timeline)

    def _update_metadata(self, value: PlaybackProperties.MetadataBean):
        # update media info
        if value.media_type == MediaType.Image:
            self._updater.type = MediaPlaybackType.IMAGE
        elif value.media_type == MediaType.Video:
            self._updater.type = MediaPlaybackType.Video
        else:
            self._updater.type = MediaPlaybackType.MUSIC
        self._updater.app_media_id = value.id_
        self._updater.music_properties.artist = ','.join(value.artist)
        self._updater.music_properties.title = value.title
        self._updater.music_properties.album_title = value.album
        self._updater.music_properties.genres = value.genre
        self._updater.thumbnail = RandomAccessStreamReference.create_from_uri(Uri(value.url))
        self._updater.update()
        # update timeline
        self._timeline.start_time = TimeSpan(0)
        self._timeline.end_time = TimeSpan(value.duration)
        self._timeline.min_seek_time = TimeSpan(0)
        self._timeline.max_seek_time = TimeSpan(value.duration)
        self._controls.update_timeline_properties(self._timeline)

    def set_tracklist_property(self, name: TrackListPropertyName, value: Any):
        pass

    def get_playback_property(self, name: PlaybackPropertyName) -> Any:
        return getattr(self._playback_properties, name.value)

    async def start(self):
        while True:
            await asyncio.sleep(1)
