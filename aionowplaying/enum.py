from enum import StrEnum


class PlaybackStatus(str, StrEnum):
    Playing = 'Playing'
    Paused = 'Paused'
    Stopped = 'Stopped'


class LoopStatus(str, StrEnum):
    None_ = 'None'
    Track = 'Track'
    Playlist = 'Playlist'
