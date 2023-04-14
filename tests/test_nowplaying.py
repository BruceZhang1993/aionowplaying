import asyncio

import pytest

import aionowplaying as aionp

PlayProp = aionp.PlaybackPropertyName


class NowPlayingInterface(aionp.NowPlayingInterface):
    NAME = 'testplayer'

    def __init__(self):
        super().__init__(self.NAME)

    def update_playback_mode(self):
        self.set_playback_property(PlayProp.LoopStatus, aionp.LoopStatus.Playlist)
        self.set_playback_property(PlayProp.Shuffle, True)

    def update_song_props(self, meta: dict):
        metadata = aionp.PlaybackProperties.MetadataBean()
        metadata.artist = meta.get('artists', ['Unknown'])
        metadata.album = meta.get('album', '')
        metadata.title = meta.get('title', '')
        metadata.cover = meta.get('artwork', '')
        metadata.url = meta.get('artwork', '')
        metadata.duration = 0
        self.set_playback_property(PlayProp.Metadata, metadata)

    def update_position(self, position):
        self.set_playback_property(PlayProp.Position, int(position * 1000))

    def update_playback_status(self):
        self.set_playback_property(PlayProp.PlaybackStatus, aionp.PlaybackStatus.Playing)

    def on_play(self):
        print('on_play')

    def on_pause(self):
        print('on_pause')

    def on_next(self):
        print('on_next')

    def on_previous(self):
        print('on_previous')

    def on_loop_status(self, status: aionp.LoopStatus):
        print('on_loop_status', status)

    def on_shuffle(self, shuffle: bool):
        print('on_shuffle', shuffle)

    def on_seek(self, offset: int):
        print('on_seek')


@pytest.fixture()
async def server():
    service = NowPlayingInterface()
    asyncio.ensure_future(service.start())
    yield service
    await asyncio.sleep(1)
    await service.stop()


async def test_update_song_props(server: NowPlayingInterface):
    server.update_song_props({
        'title': 'Hello World',
        'artists': ["hello world"],
        'album': 'Hello World'
    })
