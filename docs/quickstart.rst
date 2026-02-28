Quick Start
===========

This section will guide you through the basic usage of aionowplaying.

Installation
------------

Install via pip:

.. code-block:: shell

    pip install aionowplaying

Or using uv:

.. code-block:: shell

    uv add aionowplaying

Basic Usage
-----------

Use the factory pattern to create an instance and call ``start()``:

.. code-block:: python

    import asyncio
    import aionowplaying as aionp

    # Create instance using factory pattern
    backend = aionp.select_interface()("My Player")

    # Set player properties
    backend.set_property(aionp.PropertyName.Identity, "My Player")

    # Set playback status
    backend.set_playback_property(
        aionp.PlaybackPropertyName.PlaybackStatus,
        aionp.PlaybackStatus.Playing,
    )

    # Start the backend
    asyncio.run(backend.start())

Running in Background
---------------------

To run the backend in the background, use ``asyncio.ensure_future``:

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
        
        # Start in background
        asyncio.ensure_future(backend.start())
        
        # Do other things...
        await asyncio.sleep(10)
        
        await backend.stop()

    asyncio.run(main())

Setting Metadata
----------------

You can also set track metadata:

.. code-block:: python

    import asyncio
    import aionowplaying as aionp

    async def main():
        backend = aionp.select_interface()("My Player")
        
        # Create metadata
        metadata = aionp.PlaybackProperties.MetadataBean()
        metadata.title = "My Song"
        metadata.artist = ["Artist Name"]
        metadata.album = "Album Name"
        metadata.duration = 180000000  # in microseconds
        
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
