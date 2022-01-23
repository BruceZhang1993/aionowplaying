import time

from winrt.windows.foundation import Uri, TimeSpan
from winrt.windows.media import SystemMediaTransportControls, MediaPlaybackStatus, \
    SystemMediaTransportControlsDisplayUpdater, MediaPlaybackType, SystemMediaTransportControlsTimelineProperties
from winrt.windows.media.playback import MediaPlayer
from winrt.windows.storage.streams import RandomAccessStreamReference

if __name__ == '__main__':
    player = MediaPlayer()
    controls: SystemMediaTransportControls = player.system_media_transport_controls
    updater: SystemMediaTransportControlsDisplayUpdater = controls.display_updater
    timeline = SystemMediaTransportControlsTimelineProperties()
    # player.command_manager.is_enabled = False
    controls.is_play_enabled = True
    controls.is_pause_enabled = True
    controls.is_next_enabled = True
    controls.is_previous_enabled = True
    controls.playback_status = MediaPlaybackStatus.PLAYING
    updater.type = MediaPlaybackType.MUSIC
    updater.music_properties.artist = 'Test Artist'
    updater.music_properties.title = 'Test Title'
    updater.music_properties.album_title = 'Test Album'
    updater.thumbnail = RandomAccessStreamReference.create_from_uri(Uri(
        'https://img.moegirl.org.cn/common/3/3b/%E9%80%8F%E6%98%8E%E7%AB%8B%E7%BB%98.png'))
    updater.update()
    timeline.start_time = TimeSpan(0)
    timeline.end_time = TimeSpan(100)
    timeline.min_seek_time = TimeSpan(0)
    timeline.max_seek_time = TimeSpan(100)
    timeline.position = TimeSpan(0)
    controls.update_timeline_properties(timeline)

    position = 0

    while position < 100:
        time.sleep(1)
        position += 1
        timeline.position = TimeSpan(position)

    player.close()
