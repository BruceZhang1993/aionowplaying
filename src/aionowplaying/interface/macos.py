import asyncio
import os
from typing import Any

from Foundation import NSMutableDictionary, NSURL
from AppKit import NSImage
from MediaPlayer import MPRemoteCommandCenter, MPNowPlayingInfoCenter
from MediaPlayer import (
    MPMediaItemPropertyTitle, MPMediaItemPropertyArtist, MPMediaItemPropertyAlbumTitle,
    MPMusicPlaybackStatePlaying, MPMusicPlaybackStatePaused,
    MPMusicPlaybackStateStopped, MPMediaItemPropertyPlaybackDuration,
    MPNowPlayingInfoPropertyPlaybackRate, MPNowPlayingInfoPropertyElapsedPlaybackTime,
    MPRemoteCommandHandlerStatusSuccess, MPNowPlayingInfoPropertyDefaultPlaybackRate,
    MPMediaItemPropertyAlbumArtist, MPMediaItemPropertyComposer, MPMediaItemPropertyGenre,
    MPMediaItemPropertyArtwork,
)

try:
    from MediaPlayer import MPMediaItemPropertyAlbumTrackNumber
except Exception:  # pragma: no cover - depends on OS/framework availability
    MPMediaItemPropertyAlbumTrackNumber = None

try:
    from MediaPlayer import MPChangePlaybackPositionCommandEvent, MPChangePlaybackRateCommandEvent
    from MediaPlayer import MPChangeRepeatModeCommandEvent, MPChangeShuffleModeCommandEvent
    from MediaPlayer import MPRepeatTypeOff, MPRepeatTypeOne, MPRepeatTypeAll
    from MediaPlayer import MPShuffleTypeOff, MPShuffleTypeItems
    from MediaPlayer import MPMediaItemArtwork
except Exception:  # pragma: no cover - depends on OS/framework availability
    MPChangePlaybackPositionCommandEvent = object
    MPChangePlaybackRateCommandEvent = object
    MPChangeRepeatModeCommandEvent = object
    MPChangeShuffleModeCommandEvent = object
    MPRepeatTypeOff = None
    MPRepeatTypeOne = None
    MPRepeatTypeAll = None
    MPShuffleTypeOff = None
    MPShuffleTypeItems = None
    MPMediaItemArtwork = None

from aionowplaying import (
    BaseInterface, PlaybackPropertyName, PlaybackProperties, PlaybackStatus
)
from aionowplaying.interface.base import LoopStatus

PlaybackStatusStateMapping = {
    PlaybackStatus.Playing: MPMusicPlaybackStatePlaying,
    PlaybackStatus.Paused: MPMusicPlaybackStatePaused,
    PlaybackStatus.Stopped: MPMusicPlaybackStateStopped,
}


def create_handler(_, handler):
    def handle(_):
        asyncio.create_task(handler())
        return MPRemoteCommandHandlerStatusSuccess
    return handle


def create_event_handler(handler):
    def handle(event):
        asyncio.create_task(handler(event))
        return MPRemoteCommandHandlerStatusSuccess
    return handle


class MacOSInterface(BaseInterface):
    def __init__(self, name: str):
        super().__init__(name)
        self.cmd_center = MPRemoteCommandCenter.sharedCommandCenter()
        self.info_center = MPNowPlayingInfoCenter.defaultCenter()

        self._cmds = [
            (self.cmd_center.togglePlayPauseCommand(), self.on_play_pause),
            (self.cmd_center.playCommand(), self.on_play),
            (self.cmd_center.pauseCommand(), self.on_pause),
            (self.cmd_center.nextTrackCommand(), self.on_next),
            (self.cmd_center.previousTrackCommand(), self.on_previous),
        ]
        for cmd, handler in self._cmds:
            cmd.addTargetWithHandler_(create_handler(cmd, handler))

        # Optional commands based on MediaPlayer availability.
        self._cmd_stop = getattr(self.cmd_center, "stopCommand", lambda: None)()
        if self._cmd_stop is not None:
            self._cmd_stop.addTargetWithHandler_(create_handler(self._cmd_stop, self.on_stop))

        self._cmd_change_position = getattr(self.cmd_center, "changePlaybackPositionCommand", lambda: None)()
        if self._cmd_change_position is not None:
            self._cmd_change_position.addTargetWithHandler_(create_event_handler(self._handle_change_playback_position))

        self._cmd_change_rate = getattr(self.cmd_center, "changePlaybackRateCommand", lambda: None)()
        if self._cmd_change_rate is not None:
            self._cmd_change_rate.addTargetWithHandler_(create_event_handler(self._handle_change_playback_rate))

        self._cmd_change_repeat = getattr(self.cmd_center, "changeRepeatModeCommand", lambda: None)()
        if self._cmd_change_repeat is not None:
            self._cmd_change_repeat.addTargetWithHandler_(create_event_handler(self._handle_change_repeat_mode))

        self._cmd_change_shuffle = getattr(self.cmd_center, "changeShuffleModeCommand", lambda: None)()
        if self._cmd_change_shuffle is not None:
            self._cmd_change_shuffle.addTargetWithHandler_(create_event_handler(self._handle_change_shuffle_mode))

    def get_playback_property(self, name: PlaybackPropertyName) -> Any:
        if name == PlaybackPropertyName.Position:
            # MPNowPlayingInfoPropertyElapsedPlaybackTime is in seconds, convert to microseconds
            return self._get_property(MPNowPlayingInfoPropertyElapsedPlaybackTime) * 1000 * 1000
        if name == PlaybackPropertyName.Rate:
            return self._get_property(MPNowPlayingInfoPropertyPlaybackRate)
        return super().get_playback_property(name)

    def set_property(self, name, value: Any):
        # MPNowPlayingInfoCenter does not map player properties like fullscreen/quit/raise.
        super().set_property(name, value)

    def set_playback_property(self, name: PlaybackPropertyName, value: Any):
        if name == PlaybackPropertyName.Metadata:
            value: PlaybackProperties.MetadataBean
            nowplaying_info = self._get_or_create_nowplaying_info()
            nowplaying_info[MPMediaItemPropertyTitle] = value.title
            nowplaying_info[MPMediaItemPropertyArtist] = ', '.join(value.artist)
            nowplaying_info[MPMediaItemPropertyAlbumTitle] = value.album
            if value.albumArtist:
                nowplaying_info[MPMediaItemPropertyAlbumArtist] = ', '.join(value.albumArtist)
            if value.composer:
                nowplaying_info[MPMediaItemPropertyComposer] = ', '.join(value.composer)
            if value.genre:
                nowplaying_info[MPMediaItemPropertyGenre] = ', '.join(value.genre)
            if value.trackNumber and MPMediaItemPropertyAlbumTrackNumber is not None:
                nowplaying_info[MPMediaItemPropertyAlbumTrackNumber] = value.trackNumber
            if value.duration:
                nowplaying_info[MPMediaItemPropertyPlaybackDuration] = value.duration / 1000 / 1000
            # Artwork is supported via MPMediaItemArtwork but requires image data.
            if value.cover:
                artwork = self._load_artwork(value.cover)
                if artwork is not None:
                    nowplaying_info[MPMediaItemArtwork] = artwork
            self.info_center.setNowPlayingInfo_(nowplaying_info)
        elif name == PlaybackPropertyName.PlaybackStatus:
            value: PlaybackProperties.PlaybackStatus
            # Need to set the rate to 0 when it is paused or stopped,
            # otherwise, macos's position will be incorrect after the player resumes.
            if value in (PlaybackStatus.Paused, PlaybackStatus.Stopped):
                rate = 0
            else:
                rate = self.get_playback_property(PlaybackPropertyName.Rate)
            # Must update the position to keep it accurate. Note that updating the
            # nowplaying info re-paint the UI.
            # HELP: Is there a better way to do this?
            nowplaying_info = self._get_or_create_nowplaying_info()
            nowplaying_info[MPNowPlayingInfoPropertyElapsedPlaybackTime] = \
                self.get_playback_property(PlaybackPropertyName.Position) / 1000 / 1000
            nowplaying_info[MPNowPlayingInfoPropertyPlaybackRate] = rate
            self.info_center.setNowPlayingInfo_(nowplaying_info)
            self.info_center.setPlaybackState_(PlaybackStatusStateMapping[value])
        elif name == PlaybackPropertyName.Position:
            self._update_property(MPNowPlayingInfoPropertyElapsedPlaybackTime, value / 1000 / 1000)
        elif name == PlaybackPropertyName.Rate:
            self._update_property(MPNowPlayingInfoPropertyDefaultPlaybackRate, 1)
            self._update_property(MPNowPlayingInfoPropertyPlaybackRate, value)
        elif name == PlaybackPropertyName.Duration:
            self._update_property(MPMediaItemPropertyPlaybackDuration, value / 1000 / 1000)
        elif name == PlaybackPropertyName.LoopStatus:
            if self._cmd_change_repeat is not None and MPRepeatTypeOff is not None:
                try:
                    if value == LoopStatus.Track:
                        self._cmd_change_repeat.currentRepeatType = MPRepeatTypeOne
                    elif value == LoopStatus.Playlist:
                        self._cmd_change_repeat.currentRepeatType = MPRepeatTypeAll
                    else:
                        self._cmd_change_repeat.currentRepeatType = MPRepeatTypeOff
                except Exception:
                    # Some MediaPlayer projections expose currentRepeatType as read-only.
                    pass
        elif name == PlaybackPropertyName.Shuffle:
            if self._cmd_change_shuffle is not None and MPShuffleTypeOff is not None:
                try:
                    self._cmd_change_shuffle.currentShuffleType = (
                        MPShuffleTypeItems if value else MPShuffleTypeOff
                    )
                except Exception:
                    # Some MediaPlayer projections expose currentShuffleType as read-only.
                    pass
        elif name == PlaybackPropertyName.MinimumRate:
            self._update_supported_rates()
        elif name == PlaybackPropertyName.MaximumRate:
            self._update_supported_rates()
        elif name == PlaybackPropertyName.Volume:
            # MediaPlayer does not expose a now-playing volume control.
            pass
        else:
            # TODO: handle more properties changes
            pass
        super().set_playback_property(name, value)

        # Enable/disable commands based on capability flags.
        if name == PlaybackPropertyName.CanPlay:
            self._set_command_enabled(self.cmd_center.playCommand(), value)
        elif name == PlaybackPropertyName.CanPause:
            self._set_command_enabled(self.cmd_center.pauseCommand(), value)
            self._set_command_enabled(self.cmd_center.togglePlayPauseCommand(), value)
        elif name == PlaybackPropertyName.CanGoNext:
            self._set_command_enabled(self.cmd_center.nextTrackCommand(), value)
        elif name == PlaybackPropertyName.CanGoPrevious:
            self._set_command_enabled(self.cmd_center.previousTrackCommand(), value)
        elif name == PlaybackPropertyName.CanSeek:
            if self._cmd_change_position is not None:
                self._set_command_enabled(self._cmd_change_position, value)
        elif name == PlaybackPropertyName.CanControl:
            if self._cmd_stop is not None:
                self._set_command_enabled(self._cmd_stop, value)
            if self._cmd_change_rate is not None:
                self._set_command_enabled(self._cmd_change_rate, value)
            if self._cmd_change_repeat is not None:
                self._set_command_enabled(self._cmd_change_repeat, value)
            if self._cmd_change_shuffle is not None:
                self._set_command_enabled(self._cmd_change_shuffle, value)

    def set_tracklist_property(self, name, value: Any):
        super().set_tracklist_property(name, value)

    def get_property(self, name):
        return super().get_property(name)

    def get_tracklist_property(self, name):
        return super().get_tracklist_property(name)

    async def start(self):
        pass

    async def _handle_change_playback_position(self, event: MPChangePlaybackPositionCommandEvent):
        if not self.get_playback_property(PlaybackPropertyName.CanSeek):
            return
        position = int(event.positionTime * 1000 * 1000)
        track_id = self.get_playback_property(PlaybackPropertyName.Metadata).id_
        await self.on_set_position(track_id, position)
        await self.on_seek(position)

    async def _handle_change_playback_rate(self, event: MPChangePlaybackRateCommandEvent):
        await self.on_rate(event.playbackRate)

    async def _handle_change_repeat_mode(self, event: MPChangeRepeatModeCommandEvent):
        if not self.get_playback_property(PlaybackPropertyName.CanControl):
            return
        if MPRepeatTypeOff is None:
            return
        repeat_type = event.repeatType
        if repeat_type == MPRepeatTypeOne:
            await self.on_loop_status(LoopStatus.Track)
        elif repeat_type == MPRepeatTypeAll:
            await self.on_loop_status(LoopStatus.Playlist)
        else:
            await self.on_loop_status(LoopStatus.None_)

    async def _handle_change_shuffle_mode(self, event: MPChangeShuffleModeCommandEvent):
        if not self.get_playback_property(PlaybackPropertyName.CanControl):
            return
        if MPShuffleTypeOff is None:
            return
        shuffle_type = event.shuffleType
        await self.on_shuffle(shuffle_type == MPShuffleTypeItems)

    def _get_or_create_nowplaying_info(self):
        current = self.info_center.nowPlayingInfo()
        if current is not None:
            nowplaying_info = current.mutableCopy()
        else:
            nowplaying_info = NSMutableDictionary.dictionary()
        return nowplaying_info

    def _update_property(self, name, value):
        nowplaying_info = self._get_or_create_nowplaying_info()
        nowplaying_info[name] = value
        self.info_center.setNowPlayingInfo_(nowplaying_info)

    def _get_property(self, name):
        nowplaying_info = self._get_or_create_nowplaying_info()
        return nowplaying_info[name]

    def _set_command_enabled(self, command, enabled: bool):
        if command is None:
            return
        if hasattr(command, "enabled"):
            command.enabled = enabled
            return
        if hasattr(command, "isEnabled"):
            try:
                command.isEnabled = enabled
            except Exception:
                pass

    def _update_supported_rates(self):
        if self._cmd_change_rate is None:
            return
        min_rate = self.get_playback_property(PlaybackPropertyName.MinimumRate)
        max_rate = self.get_playback_property(PlaybackPropertyName.MaximumRate)
        if min_rate is None or max_rate is None or min_rate > max_rate:
            return
        rates = sorted(set([min_rate, 1.0, max_rate]))
        try:
            self._cmd_change_rate.supportedPlaybackRates = rates
        except Exception:
            # Some MediaPlayer projections expose supportedPlaybackRates as read-only.
            return

    def _load_artwork(self, cover: str):
        # MediaPlayer expects image data; remote URLs may block. Only load local files.
        if cover.startswith("file://"):
            url = NSURL.URLWithString_(cover)
        elif os.path.exists(cover):
            url = NSURL.fileURLWithPath_(cover)
        else:
            return None
        image = NSImage.alloc().initWithContentsOfURL_(url)
        if image is None:
            return None
        if MPMediaItemArtwork is None:
            return None
        return MPMediaItemArtwork.alloc().initWithBoundsSize_requestHandler_(image.size(), lambda _: image)
