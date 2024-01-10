import asyncio
import threading
from typing import Any
from datetime import timedelta

from winsdk.system import Array
from winsdk.windows.foundation import Uri
from winsdk.windows.foundation.collections import IVector
from winsdk.windows.media import SystemMediaTransportControlsTimelineProperties, SystemMediaTransportControls, \
    SystemMediaTransportControlsDisplayUpdater, MediaPlaybackStatus, MediaPlaybackType, MediaPlaybackAutoRepeatMode, \
    AutoRepeatModeChangeRequestedEventArgs, SystemMediaTransportControlsButtonPressedEventArgs, \
    SystemMediaTransportControlsButton, PlaybackPositionChangeRequestedEventArgs, PlaybackRateChangeRequestedEventArgs, \
    SystemMediaTransportControlsPropertyChangedEventArgs, SystemMediaTransportControlsProperty, \
    ShuffleEnabledChangeRequestedEventArgs
from winsdk.windows.media.playback import MediaPlayer
from winsdk.windows.storage.streams import RandomAccessStreamReference

from aionowplaying import BaseInterface, PropertyName, PlaybackPropertyName
from aionowplaying.interface.base import TrackListPropertyName, PlaybackStatus, PlaybackProperties, LoopStatus, \
    MediaType


def TimeSpan(x_microsec):
    return timedelta(microseconds=x_microsec)


class WindowsInterface(BaseInterface):
    def __init__(self, name):
        super(WindowsInterface, self).__init__(name)
        self._loop = asyncio.get_event_loop()
        self._running = True
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
        if asyncio.iscoroutinefunction(self.on_shuffle):
            self._run_task(self.on_shuffle(shuffle_enabled))
        else:
            self.on_shuffle(shuffle_enabled)

    def property_changed(self, _, args: SystemMediaTransportControlsPropertyChangedEventArgs):
        property_: SystemMediaTransportControlsProperty = args.property
        if property_ == SystemMediaTransportControlsProperty.SOUND_LEVEL:
            if asyncio.iscoroutinefunction(self.on_volume):
                self._run_task(self.on_volume(self._controls.sound_level))
            else:
                self.on_volume(self._controls.sound_level)

    def playback_rate_change_requested(self, _, args: PlaybackRateChangeRequestedEventArgs):
        rate: float = args.requested_playback_rate
        if asyncio.iscoroutinefunction(self.on_rate):
            self._run_task(self.on_rate(rate))
        else:
            self.on_rate(rate)

    def playback_position_change_requested(self, _, args: PlaybackPositionChangeRequestedEventArgs):
        position = args.requested_playback_position
        position = position.seconds * 1000 * 1000 + position.microseconds

        if self._playback_properties.CanSeek:
            if asyncio.iscoroutinefunction(self.on_set_position):
                self._run_task(self.on_set_position(self._playback_properties.Metadata.id_, position))
            else:
                self.on_set_position(self._playback_properties.Metadata.id_, position)

            if asyncio.iscoroutinefunction(self.on_seek):
                self._run_task(self.on_seek(position))
            else:
                self.on_seek(position)


    def button_pressed(self, _, args: SystemMediaTransportControlsButtonPressedEventArgs):
        button: SystemMediaTransportControlsButton = args.button
        if button == SystemMediaTransportControlsButton.PLAY and self._playback_properties.CanPlay:
            if asyncio.iscoroutinefunction(self.on_play):
                self._run_task(self.on_play())
            else:
                self.on_play()
            self._controls.playback_status = MediaPlaybackStatus.PLAYING
            self._playback_properties.PlaybackStatus = PlaybackStatus.Playing
        if button == SystemMediaTransportControlsButton.PAUSE and self._playback_properties.CanPause:
            if asyncio.iscoroutinefunction(self.on_pause):
                self._run_task(self.on_pause())
            else:
                self.on_pause()
            self._controls.playback_status = MediaPlaybackStatus.PAUSED
            self._playback_properties.PlaybackStatus = PlaybackStatus.Paused
        if button == SystemMediaTransportControlsButton.NEXT and self._playback_properties.CanGoNext:
            if asyncio.iscoroutinefunction(self.on_next):
                self._run_task(self.on_next())
            else:
                self.on_next()
        if button == SystemMediaTransportControlsButton.PREVIOUS and self._playback_properties.CanGoPrevious:
            if asyncio.iscoroutinefunction(self.on_previous):
                self._run_task(self.on_previous())
            else:
                self.on_previous()
        if button == SystemMediaTransportControlsButton.STOP and self._playback_properties.CanControl:
            if asyncio.iscoroutinefunction(self.on_stop):
                self._run_task(self.on_stop())
            else:
                self.on_stop()

    def auto_repeat_mode_change_requested(self, _, args: AutoRepeatModeChangeRequestedEventArgs):
        value = LoopStatus.None_
        mode: MediaPlaybackAutoRepeatMode = args.requested_auto_repeat_mode
        if mode == MediaPlaybackAutoRepeatMode.LIST:
            value = LoopStatus.Playlist
        elif mode == MediaPlaybackAutoRepeatMode.TRACK:
            value = LoopStatus.Track
        if asyncio.iscoroutinefunction(self.on_loop_status):
            self._run_task(self.on_loop_status(value))
        else:
            self.on_loop_status(value)
        self._playback_properties.LoopStatus = value

    def set_property(self, name: PropertyName, value: Any):
        pass

    def set_playback_property(self, name: PlaybackPropertyName, value: Any):
        if name == PlaybackPropertyName.CanControl:
            self._controls.is_stop_enabled = value
            self._playback_properties.CanControl = value
        elif name == PlaybackPropertyName.CanPlay:
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
        elif name == PlaybackPropertyName.CanSeek:
            self._playback_properties.CanSeek = value
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
            self._controls.shuffle_enabled = value
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
        elif name == PlaybackPropertyName.Duration:
            self._timeline.end_time = TimeSpan(value)
            self._timeline.max_seek_time = TimeSpan(value)
            self._controls.update_timeline_properties(self._timeline)

    def _update_metadata(self, value: PlaybackProperties.MetadataBean):
        # update media info
        if value.media_type == MediaType.Image:
            self._updater.type = MediaPlaybackType.IMAGE
        elif value.media_type == MediaType.Video:
            self._updater.type = MediaPlaybackType.VIDEO
        else:
            self._updater.type = MediaPlaybackType.MUSIC
        
        self._updater.app_media_id = value.id_
        
        self._updater.music_properties.artist = ','.join(value.artist)
        self._updater.music_properties.title = value.title
        self._updater.music_properties.album_title = value.album
        # self._updater.music_properties.genres: IVector
        # fixme: implement genres field
        # self._updater.music_properties.genres.replace_all(Array('u', 8))
        if value.cover:  # not None and not empty
            self._updater.thumbnail = RandomAccessStreamReference.create_from_uri(Uri(value.cover))
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
        # Don't need a background server for Windows
        pass

    async def stop(self):
        self._running = False

    def _run_task(self, task):
        # Windows callbacks may be invoked in non-main thread, besides,
        # they may run in different threads.
        if threading.current_thread() is not threading.main_thread():
            asyncio.run_coroutine_threadsafe(task, self._loop)
        else:
            asyncio.create_task(task)
