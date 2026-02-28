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

使用工厂模式创建实例并调用 ``start()``：

.. code-block:: python

    import asyncio
    import aionowplaying as aionp

    # 使用工厂模式创建实例
    backend = aionp.select_interface()("My Player")

    # 设置播放器属性
    backend.set_property(aionp.PropertyName.Identity, "My Player")

    # 设置播放状态
    backend.set_playback_property(
        aionp.PlaybackPropertyName.PlaybackStatus,
        aionp.PlaybackStatus.Playing,
    )

    # 启动后端
    asyncio.run(backend.start())

后台运行
---------------------

要以后台方式运行后端，请使用 ``asyncio.ensure_future``：

.. code-block:: python

    import asyncio
    import aionowplaying as aionp

    async def main():
        backend = aionp.select_interface()("My Player")
        backend.set_property(aionp.PropertyName.Identity, "My Player")
        backend.set_playback_property(
            aionp.PlaybackPropertyName.PlaybackStatus,
            aionp.PlaybackStatus.Playing,
        )
        
        # 后台启动
        asyncio.ensure_future(backend.start())
        
        # 做其他事情...
        await asyncio.sleep(10)
        
        await backend.stop()

    asyncio.run(main())

设置元数据
----------------

您还可以设置曲目元数据：

.. code-block:: python

    import asyncio
    import aionowplaying as aionp

    async def main():
        backend = aionp.select_interface()("My Player")
        
        # 创建元数据
        metadata = aionp.PlaybackProperties.MetadataBean()
        metadata.title = "我的歌曲"
        metadata.artist = ["艺术家名称"]
        metadata.album = "专辑名称"
        metadata.duration = 180000000  # 微秒
        
        backend.set_playback_property(
            aionp.PlaybackPropertyName.Metadata,
            metadata
        )
        backend.set_playback_property(
            aionp.PlaybackPropertyName.PlaybackStatus,
            aionp.PlaybackStatus.Playing,
        )
        
        await backend.start()

    asyncio.run(main())
