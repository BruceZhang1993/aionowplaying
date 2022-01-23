from enum import Enum
from typing import Any, List
from pydantic import BaseModel


class TrackListPropertyName(str, Enum):
    Tracks = 'Tracks'
    CanEditTracks = 'CanEditTracks'


class PropertyName(str, Enum):
    CanQuit = "CanQuit"
    CanSetFullscreen = "CanSetFullscreen"
    CanRaise = "CanRaise"
    HasTrackList = "HasTrackList"
    Identity = "Identity"
    DesktopEntry = "DesktopEntry"
    SupportedUriSchemes = "SupportedUriSchemes"
    SupportedMimeTypes = "SupportedMimeTypes"
    Fullscreen = "Fullscreen"


class PlaybackPropertyName(str, Enum):
    PlaybackStatus = "PlaybackStatus"
    LoopStatus = "LoopStatus"
    Rate = "Rate"
    Shuffle = "Shuffle"
    Metadata = "Metadata"
    Volume = "Volume"
    Position = "Position"
    MinimumRate = "MinimumRate"
    MaximumRate = "MaximumRate"
    CanGoNext = "CanGoNext"
    CanGoPrevious = "CanGoPrevious"
    CanPlay = "CanPlay"
    CanPause = "CanPause"
    CanSeek = "CanSeek"
    CanControl = "CanControl"


class PlaybackStatus(str, Enum):
    Playing = "Playing"
    Paused = "Paused"
    Stopped = "Stopped"


class LoopStatus(str, Enum):
    None_ = "None"
    Track = "Track"
    Playlist = "Playlist"


class TrackListProperties(BaseModel):
    Tracks: List[str] = []
    CanEditTracks: bool = False


class PlayerProperties(BaseModel):
    Fullscreen: bool = False
    CanQuit: bool = False
    CanSetFullscreen: bool = False
    CanRaise: bool = False
    HasTrackList: bool = False
    Identity: str = ""
    DesktopEntry: str = ""
    SupportedUriSchemes: List[str] = []
    SupportedMimeTypes: List[str] = []


class PlaybackProperties(BaseModel):
    class MetadataBean(BaseModel):
        id_: str = ''
        duration: int = 0  # in microseconds
        cover: str = ''
        album: str = ''
        albumArtist: List[str] = []
        artist: List[str] = []
        lyrics: str = ''
        comments: List[str] = []
        composer: List[str] = []
        genre: List[str] = []
        lyricist: List[str] = []
        title: str = "Unknown"
        trackNumber: int = 0
        url: str = ''

    PlaybackStatus: 'PlaybackStatus' = PlaybackStatus.Stopped
    LoopStatus: 'LoopStatus' = LoopStatus.None_
    Rate: float = 1.0
    Shuffle: bool = False
    Metadata: MetadataBean = MetadataBean()
    Volume: float = 1.0
    Position: int = 0  # in microseconds
    MinimumRate: float = 1.0
    MaximumRate: float = 1.0
    CanGoNext: bool = False
    CanGoPrevious: bool = False
    CanPlay: bool = False
    CanPause: bool = False
    CanSeek: bool = False
    CanControl: bool = False


class BaseInterface:
    def __init__(self, name: str):
        pass

    def start(self):
        pass

    async def on_fullscreen(self, fullscreen: bool):
        pass

    async def on_raise(self):
        pass

    async def on_quit(self):
        pass

    async def on_loop_status(self, status: LoopStatus):
        pass

    async def on_rate(self, rate: float):
        pass

    async def on_shuffle(self, shuffle: bool):
        pass

    async def on_volume(self, volume: float):
        pass

    async def on_next(self):
        pass

    async def on_previous(self):
        pass

    async def on_pause(self):
        pass

    async def on_play_pause(self):
        pass

    async def on_play(self):
        pass

    async def on_stop(self):
        pass

    async def on_seek(self, offset: int):
        pass

    async def on_open_uri(self, uri: str):
        pass

    async def on_set_position(self, track_id: str, position: int):
        pass

    async def seeked(self, position: int):
        pass

    def set_property(self, name: PropertyName, value: Any):
        pass

    def set_playback_property(self, name: PlaybackPropertyName, value: Any):
        pass

    def set_tracklist_property(self, name: TrackListPropertyName, value: Any):
        pass
