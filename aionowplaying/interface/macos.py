import asyncio
from typing import Any

from Foundation import NSMutableDictionary
from MediaPlayer import MPRemoteCommandCenter, MPNowPlayingInfoCenter
from MediaPlayer import (
    MPMediaItemPropertyTitle, MPMediaItemPropertyArtist, MPMediaItemPropertyAlbumTitle,
    MPMusicPlaybackStatePlaying, MPMusicPlaybackStatePaused,
    MPMusicPlaybackStateStopped, MPMediaItemPropertyPlaybackDuration,
    MPNowPlayingInfoPropertyPlaybackRate, MPNowPlayingInfoPropertyElapsedPlaybackTime,
    MPRemoteCommandHandlerStatusSuccess, MPNowPlayingInfoPropertyDefaultPlaybackRate,
)

from aionowplaying import (
    BaseInterface, PlaybackPropertyName, PlaybackProperties, PlaybackStatus
)

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

    def set_playback_property(self, name: PlaybackPropertyName, value: Any):
        if name == PlaybackPropertyName.Metadata:
            value: PlaybackProperties.MetadataBean
            nowplaying_info = self._get_or_create_nowplaying_info()
            nowplaying_info[MPMediaItemPropertyTitle] = value.title
            nowplaying_info[MPMediaItemPropertyArtist] = ', '.join(value.artist)
            nowplaying_info[MPMediaItemPropertyAlbumTitle] = value.album
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
        else:
            # TODO: handle more properties changes
            pass

    async def start(self):
        pass

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
