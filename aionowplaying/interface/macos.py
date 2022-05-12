from typing import Any

from aionowplaying import BaseInterface, PlaybackPropertyName, PlaybackProperties

from Foundation import NSRunLoop, NSMutableDictionary, NSObject
from MediaPlayer import MPRemoteCommandCenter, MPNowPlayingInfoCenter
from MediaPlayer import (
    MPMediaItemPropertyTitle, MPMediaItemPropertyArtist, MPMediaItemPropertyAlbumTitle,
    MPMusicPlaybackState, MPMusicPlaybackStatePlaying, MPMusicPlaybackStatePaused, MPMusicPlaybackStateStopped
)


class MacOSInterface(BaseInterface):
    def __init__(self, name: str):
        super(MacOSInterface, self).__init__(name)
        self.cmd_center = MPRemoteCommandCenter.sharedCommandCenter()
        self.info_center = MPNowPlayingInfoCenter.defaultCenter()

        cmds = [
            self.cmd_center.togglePlayPauseCommand(),
            self.cmd_center.playCommand(),
            self.cmd_center.pauseCommand(),
        ]

        for cmd in cmds:
            cmd.addTargetWithHandler_(self._create_handler(cmd))

    def _create_handler(self, _):
        def handle(event):
            if event.command() == self.cmd_center.pauseCommand():
                self.info_center.setPlaybackState_(MPMusicPlaybackStatePaused)
            elif event.command() == self.cmd_center.playCommand():
                self.info_center.setPlaybackState_(MPMusicPlaybackStatePlaying)
            return 0
        return handle

    def set_playback_property(self, name: PlaybackPropertyName, value: Any):
        if name == PlaybackPropertyName.Metadata:
            value: PlaybackProperties.MetadataBean
            nowplaying_info = NSMutableDictionary.dictionary()
            nowplaying_info[MPMediaItemPropertyTitle] = value.title
            nowplaying_info[MPMediaItemPropertyArtist] = ', '.join(value.artist)
            nowplaying_info[MPMediaItemPropertyAlbumTitle] = value.album
            self.info_center.setNowPlayingInfo_(nowplaying_info)
        if name == PlaybackPropertyName.PlaybackStatus:
            value: PlaybackProperties.PlaybackStatus
            if value == PlaybackProperties.PlaybackStatus.Playing:
                self.info_center.setPlaybackState_(MPMusicPlaybackStatePlaying)
            elif value == PlaybackProperties.PlaybackStatus.Paused:
                self.info_center.setPlaybackState_(MPMusicPlaybackStatePaused)
            elif value == PlaybackProperties.PlaybackStatus.Stopped:
                self.info_center.setPlaybackState_(MPMusicPlaybackStateStopped)
        if name == PlaybackPropertyName.Position:
            value: int
            self.info_center.setElapsedPlaybackTime_(int(value / 1000))
        if name == PlaybackPropertyName.Shuffle:
            value: bool

    def start(self):
        NSRunLoop.mainRunLoop().run()
