import asyncio
import sys
import pytest

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason=f'These tests should be skipped on {sys.platform}')

from aionowplaying import NowPlayingInterface, PlaybackPropertyName, PlaybackStatus, PlaybackProperties


class MyWindowsNowPlayingInterface(NowPlayingInterface):
    async def on_play(self):
        print('on_play')

    async def on_pause(self):
        print('on_pause')

    async def on_next(self):
        print('on_next')

    async def on_previous(self):
        print('on_preview')


@pytest.yield_fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
def interface() -> MyWindowsNowPlayingInterface:
    it = MyWindowsNowPlayingInterface('TestNowPlayingPlayer')
    assert it is not None
    task = asyncio.ensure_future(it.start())
    yield it
    task.cancel()


class TestWindowsNowPlaying:
    async def test_now_playing(self, interface):
        interface.set_playback_property(PlaybackPropertyName.CanPlay, True)
        interface.set_playback_property(PlaybackPropertyName.CanPause, True)
        interface.set_playback_property(PlaybackPropertyName.CanGoNext, True)
        interface.set_playback_property(PlaybackPropertyName.CanGoPrevious, True)
        interface.set_playback_property(PlaybackPropertyName.PlaybackStatus, PlaybackStatus.Playing)
        metadata = PlaybackProperties.MetadataBean()
        metadata.artist = ['Azusa', 'Nanami']
        metadata.album = 'Azusa collection'
        metadata.title = 'Azusa Music'
        metadata.url = 'https://img.moegirl.org.cn/common/3/3b/%E9%80%8F%E6%98%8E%E7%AB%8B%E7%BB%98.png'
        interface.set_playback_property(PlaybackPropertyName.Metadata, metadata)
        await asyncio.sleep(20)
