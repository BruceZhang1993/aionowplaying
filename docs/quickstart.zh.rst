快速开始
===========

本节将引导您了解 aionowplaying 的基本用法。

安装
------------

通过 pip 安装：

.. code-block:: shell

    pip install aionowplaying

或使用 uv：

.. code-block:: shell

    uv add aionowplaying

基本用法
-----------

使用 ``NowPlaying`` 类获得简化的接口：

.. code-block:: python

    import asyncio
    from datetime import timedelta
    from aionowplaying import NowPlaying

    # 创建播放器并设置元数据和回调
    player = NowPlaying(
        "My Player",
        metadata={
            "title": "歌曲名称",
            "artist": ["艺术家"],
            "album": "专辑",
            "duration": timedelta(minutes=3, seconds=30),
        },
        on_play=lambda: my_player.play(),
        on_pause=lambda: my_player.pause(),
        on_next=lambda: my_player.next(),
    )

    # 播放过程中更新元数据
    player.title = "新歌曲"
    player.position = timedelta(seconds=60)
    player.set_playing()

    # 启动后端
    asyncio.run(player.start())

后台运行
---------------------

要以后台方式运行后端，请使用 ``asyncio.ensure_future``：

.. code-block:: python

    import asyncio
    from datetime import timedelta
    from aionowplaying import NowPlaying

    async def main():
        player = NowPlaying(
            "My Player",
            metadata={
                "title": "歌曲名称",
                "artist": ["艺术家"],
                "duration": timedelta(minutes=3),
            },
            on_play=lambda: my_player.play(),
            on_pause=lambda: my_player.pause(),
        )

        # 后台启动
        asyncio.ensure_future(player.start())

        # 做其他事情...
        await asyncio.sleep(10)

        await player.stop()

    asyncio.run(main())

可用属性
--------------------

``NowPlaying`` 类提供便捷的属性访问器：

**元数据属性：**

- ``title`` - 曲目标题
- ``artist`` - 艺术家列表（接受字符串或列表）
- ``album`` - 专辑名称
- ``album_artist`` - 专辑艺术家
- ``cover`` - 封面图片 URL
- ``url`` - 曲目 URL
- ``track_number`` - 曲目编号
- ``duration`` - 曲目时长，类型为 ``timedelta``

**播放状态属性：**

- ``position`` - 当前播放位置，类型为 ``timedelta``
- ``volume`` - 音量（0.0 到 1.0）
- ``shuffle`` - 随机播放模式（布尔值）
- ``loop_status`` - 循环模式（``LoopStatus.None_``、``LoopStatus.Track``、``LoopStatus.Playlist``）
- ``rate`` - 播放速率

**状态方法：**

- ``set_playing()`` - 设置播放状态为正在播放
- ``set_paused()`` - 设置播放状态为已暂停
- ``set_stopped()`` - 设置播放状态为已停止

**只读属性：**

- ``is_playing`` - 当前是否正在播放
- ``is_paused`` - 当前是否已暂停
- ``is_stopped`` - 当前是否已停止

回调函数
---------

您可以注册媒体控制事件的回调函数：

.. code-block:: python

    from aionowplaying import NowPlaying, LoopStatus

    player = NowPlaying(
        "My Player",
        on_play=lambda: player.play(),
        on_pause=lambda: player.pause(),
        on_next=lambda: player.next_track(),
        on_previous=lambda: player.previous_track(),
        on_stop=lambda: player.stop(),
        on_seek=lambda pos: player.seek(pos),  # pos 是 timedelta
        on_volume=lambda vol: player.set_volume(vol),  # vol 是 0.0-1.0 的浮点数
        on_shuffle=lambda enabled: player.set_shuffle(enabled),  # enabled 是布尔值
        on_loop=lambda status: player.set_loop(status),  # status 是 LoopStatus
    )

能力标志会根据您提供的回调函数自动推断。例如，如果您提供了 ``on_play``，
则 ``CanPlay`` 会自动设置为 ``True``。

高级用法
--------------

如需更精细的控制，可以继承 ``BaseInterface``：

.. code-block:: python

    from aionowplaying import BaseInterface

    class MyPlayer(BaseInterface):
        async def on_play(self):
            # 自定义实现
            pass

        async def on_pause(self):
            # 自定义实现
            pass

.. note::

    ``select_interface()`` 函数和 ``NowPlayingInterface`` 别名已废弃。
    请使用 ``NowPlaying`` 替代。