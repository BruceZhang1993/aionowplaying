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


class MediaType(str, Enum):
    Music = "Music"
    Video = "Video"
    Image = "Image"


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
        media_type: 'MediaType' = MediaType.Music
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

    async def start(self):
        """
        Call this method to start nowplaying backend.
        Wrap with :meth:`asyncio.ensure_future` if you want to run in background.
        """
        pass

    async def on_fullscreen(self, fullscreen: bool):
        """
        This will be called when nowplaying backend want to set player fullscreen state.
        This will only be called if you set :attr:`PlayerProperties.CanSetFullscreen` to True.
        :param fullscreen: True if fullscreen, False otherwise.
        :type fullscreen: bool
        """
        pass

    async def on_raise(self):
        """
        This will be called when nowplaying backend want to raise player window.
        This will only be called if you set :attr:`PlayerProperties.CanRaise` to True.
        """
        pass

    async def on_quit(self):
        """
        This will be called when nowplaying backend want to quit player.
        This will only be called if you set :attr:`PlayerProperties.CanQuit` to True.
        """
        pass

    async def on_loop_status(self, status: LoopStatus):
        """
        This will be called when nowplaying backend want to set loop status.
        This will only be called if you set :attr:`PlaybackProperties.CanControl` to True.
        :param status: Loop status.
        :type status: LoopStatus
        """
        pass

    async def on_rate(self, rate: float):
        """
        This will be called when nowplaying backend want to set playback rate.
        The rate is a float value between :attr:`PlaybackProperties.MinimumRate`
        and :attr:`PlaybackProperties.MaximumRate`.
        :param rate: Playback rate.
        :type rate: float
        """
        pass

    async def on_shuffle(self, shuffle: bool):
        """
        This will be called when nowplaying backend want to set shuffle status.
        This will only be called if you set :attr:`PlaybackProperties.CanControl` to True.
        :param shuffle: True if shuffle, False otherwise.
        :type shuffle: bool
        """
        pass

    async def on_volume(self, volume: float):
        """
        This will be called when nowplaying backend want to set playback volume.
        This will only be called if you set :attr:`PlaybackProperties.CanControl` to True.
        :param volume: Volume value between 0.0 and 1.0 (both inclusive).
        :type volume: float
        """
        pass

    async def on_next(self):
        """
        This will be called when nowplaying backend want to play next track.
        This will only be called if you set :attr:`PlaybackProperties.CanGoNext` to True.
        """
        pass

    async def on_previous(self):
        """
        This will be called when nowplaying backend want to play previous track.
        This will only be called if you set :attr:`PlaybackProperties.CanGoPrevious` to True.
        """
        pass

    async def on_pause(self):
        """
        This will be called when nowplaying backend want to pause playback.
        This will only be called if you set :attr:`PlaybackProperties.CanPause` to True.
        """
        pass

    async def on_play_pause(self):
        """
        This will be called when nowplaying backend want to play or pause playback.
        This will only be called if you set :attr:`PlaybackProperties.CanPause` to True.
        """
        if self.get_playback_property(PlaybackPropertyName.PlaybackStatus) == PlaybackStatus.Playing:
            await self.on_pause()
            self.set_playback_property(PlaybackPropertyName.PlaybackStatus, PlaybackStatus.Paused)
        else:
            await self.on_play()
            self.set_playback_property(PlaybackPropertyName.PlaybackStatus, PlaybackStatus.Playing)

    async def on_play(self):
        """
        This will be called when nowplaying backend want to play playback.
        This will only be called if you set :attr:`PlaybackProperties.CanPlay` to True.
        """
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

    def get_property(self, name: PropertyName) -> Any:
        pass

    def get_playback_property(self, name: PlaybackPropertyName) -> Any:
        pass

    def get_tracklist_property(self, name: TrackListPropertyName) -> Any:
        pass
