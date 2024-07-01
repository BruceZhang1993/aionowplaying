import asyncio
from typing import List

from Foundation import NSMutableDictionary
from MediaPlayer import MPRemoteCommandCenter, MPNowPlayingInfoCenter
from MediaPlayer import (
    MPMediaItemPropertyTitle, MPMediaItemPropertyArtist, MPMediaItemPropertyAlbumTitle,
    MPMusicPlaybackStatePlaying, MPMusicPlaybackStatePaused,
    MPMusicPlaybackStateStopped, MPMediaItemPropertyPlaybackDuration,
    MPNowPlayingInfoPropertyPlaybackRate, MPNowPlayingInfoPropertyElapsedPlaybackTime,
    MPRemoteCommandHandlerStatusSuccess, MPNowPlayingInfoPropertyDefaultPlaybackRate,
)

from aionowplaying.enum import PlaybackStatus
from aionowplaying.interface import MPInterface, MPPlayerInterface, MPTrackListInterface

PlaybackStatusStateMapping = {
    PlaybackStatus.Playing: MPMusicPlaybackStatePlaying,
    PlaybackStatus.Paused: MPMusicPlaybackStatePaused,
    PlaybackStatus.Stopped: MPMusicPlaybackStateStopped,
}

from aionowplaying.backend import BaseNowPlayingBackend


def create_handler(_, handler):
    def handle(_):
        asyncio.create_task(handler())
        return MPRemoteCommandHandlerStatusSuccess

    return handle


class MacOSNowPlayingBackend(BaseNowPlayingBackend):
    @staticmethod
    def target_platforms() -> List[str]:
        return ['darwin']

    def __init__(self, interface: MPInterface, player_interface: MPPlayerInterface,
                 tracklist_interface: MPTrackListInterface):
        super().__init__(interface, player_interface, tracklist_interface)
        self.cmd_center = MPRemoteCommandCenter.sharedCommandCenter()
        self.info_center = MPNowPlayingInfoCenter.defaultCenter()

        self._cmds = [
            (self.cmd_center.togglePlayPauseCommand(), self._player_interface.playPause),
            (self.cmd_center.playCommand(), self._player_interface.play),
            (self.cmd_center.pauseCommand(), self._player_interface.pause),
            (self.cmd_center.nextTrackCommand(), self._player_interface.next),
            (self.cmd_center.previousTrackCommand(), self._player_interface.previous),
        ]
        for cmd, handler in self._cmds:
            cmd.addTargetWithHandler_(create_handler(cmd, handler))

    def run(self):
        pass

    def destroy(self):
        pass
