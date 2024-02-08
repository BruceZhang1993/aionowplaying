from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class Metadata:
    trackId: str
    length: int  # Duration in microseconds
    artUrl: str
    album: str
    albumArtist: List[str]
    artist: List[str]
    asText: str  # Track lyrics (should not include timeline)
    audioBPM: int  # The speed of the music, in beats per minute
    autoRating: float  # An automatically-generated rating (0.0-1.0)
    comment: List[str]
    composer: List[str]
    contentCreated: datetime
    discNumber: int  # The disc number on the album that this track is from
    firstUsed: datetime  # When the track was first played.
    lastUsed: datetime  # When the track was last played.
    genre: List[str]
    lyricist: List[str]
    title: str
    trackNumber: int
    url: str
    useCount: int
    userRating: float
