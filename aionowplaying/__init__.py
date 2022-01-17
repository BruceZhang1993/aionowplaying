import sys
from typing import Type

from aionowplaying.interface import select_interface, BaseInterface
from aionowplaying.interface.base import PropertyName, LoopStatus, PlaybackPropertyName, PlaybackProperties, \
    PlaybackStatus

NowPlayingInterface: Type[BaseInterface] = select_interface()
if NowPlayingInterface is None:
    raise NotImplemented()


class MyNowPlayingInterface(NowPlayingInterface):
    async def on_raise(self):
        print('on_raise')

    async def on_quit(self):
        print('on_quit')
        sys.exit(0)

    async def on_loop_status(self, status: LoopStatus):
        print('on_loop_status', status)

    async def on_rate(self, rate: float):
        print('on_rate', rate)

    async def on_shuffle(self, shuffle: bool):
        print('on_shuffle', shuffle)

    async def on_volume(self, volume: float):
        print('on_volume', volume)

    async def on_next(self):
        print('on_next')

    async def on_previous(self):
        print('on_previous')

    async def on_play(self):
        print('on_play')

    async def on_play_pause(self):
        print('on_play_pause')

    async def on_stop(self):
        print('on_stop')

    async def on_seek(self, offset: int):
        print('on_seek', offset)


if __name__ == '__main__':
    it = MyNowPlayingInterface('test_aionowplaying')
    it.set_property(PropertyName.CanQuit, True)
    it.set_property(PropertyName.CanRaise, True)
    it.set_playback_property(PlaybackPropertyName.CanGoNext, True)
    it.set_playback_property(PlaybackPropertyName.CanGoPrevious, True)
    it.set_playback_property(PlaybackPropertyName.CanPlay, True)
    it.set_playback_property(PlaybackPropertyName.CanPause, True)
    it.set_playback_property(PlaybackPropertyName.CanSeek, True)
    it.set_playback_property(PlaybackPropertyName.PlaybackStatus, PlaybackStatus.Playing)
    metadata = PlaybackProperties.MetadataBean()
    metadata.id_ = 'test_123456'
    metadata.album = '测试专辑'
    metadata.artist = ['测试歌手1', '测试歌手2']
    metadata.lyrics = '123'
    metadata.genre = ['Pop']
    metadata.albumArtist = ['测试歌手1', '测试歌手2']
    metadata.title = '测试标题'
    metadata.cover = 'file:///home/bruce/Pictures/photo_2021-12-24_01-04-55.jpg'
    metadata.duration = 10000
    it.set_playback_property(PlaybackPropertyName.Metadata, metadata)

    import asyncio


    async def job1():
        await asyncio.sleep(10)
        metadata = PlaybackProperties.MetadataBean()
        metadata.id_ = 'test_123'
        metadata.album = '测试专辑123'
        metadata.artist = ['测试歌手2']
        metadata.lyrics = '123123'
        metadata.genre = ['Pop']
        metadata.albumArtist = ['测试歌手2']
        metadata.title = '标题2'
        metadata.cover = 'file:///home/bruce/Pictures/photo_2021-12-24_01-04-55.jpg'
        metadata.duration = 20000
        it.set_playback_property(PlaybackPropertyName.Metadata, metadata)


    async def main():
        return await asyncio.gather(it.start(), job1())


    asyncio.run(main())
