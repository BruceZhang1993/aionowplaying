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

Use the ``NowPlaying`` class for a simplified interface:

.. code-block:: python

    import asyncio
    from datetime import timedelta
    from aionowplaying import NowPlaying

    # Create player with metadata and callbacks
    player = NowPlaying(
        "My Player",
        metadata={
            "title": "Song Name",
            "artist": ["Artist"],
            "album": "Album",
            "duration": timedelta(minutes=3, seconds=30),
        },
        on_play=lambda: my_player.play(),
        on_pause=lambda: my_player.pause(),
        on_next=lambda: my_player.next(),
    )

    # Update metadata during playback
    player.title = "New Song"
    player.position = timedelta(seconds=60)
    player.set_playing()

    # Start the backend
    asyncio.run(player.start())

Running in Background
---------------------

To run the backend in the background, use ``asyncio.ensure_future``:

.. code-block:: python

    import asyncio
    from datetime import timedelta
    from aionowplaying import NowPlaying

    async def main():
        player = NowPlaying(
            "My Player",
            metadata={
                "title": "Song Name",
                "artist": ["Artist"],
                "duration": timedelta(minutes=3),
            },
            on_play=lambda: my_player.play(),
            on_pause=lambda: my_player.pause(),
        )

        # Start in background
        asyncio.ensure_future(player.start())

        # Do other things...
        await asyncio.sleep(10)

        await player.stop()

    asyncio.run(main())

Available Properties
--------------------

The ``NowPlaying`` class provides convenient property accessors:

**Metadata Properties:**

- ``title`` - Track title
- ``artist`` - List of artists (accepts string or list)
- ``album`` - Album name
- ``album_artist`` - Album artist(s)
- ``cover`` - Cover art URL
- ``url`` - Track URL
- ``track_number`` - Track number
- ``duration`` - Track duration as ``timedelta``

**Playback State Properties:**

- ``position`` - Current position as ``timedelta``
- ``volume`` - Volume level (0.0 to 1.0)
- ``shuffle`` - Shuffle mode (bool)
- ``loop_status`` - Loop mode (``LoopStatus.None_``, ``LoopStatus.Track``, ``LoopStatus.Playlist``)
- ``rate`` - Playback rate

**State Methods:**

- ``set_playing()`` - Set playback status to Playing
- ``set_paused()`` - Set playback status to Paused
- ``set_stopped()`` - Set playback status to Stopped

**Read-only Properties:**

- ``is_playing`` - True if currently playing
- ``is_paused`` - True if currently paused
- ``is_stopped`` - True if currently stopped

Callbacks
---------

You can register callbacks for media control events:

.. code-block:: python

    from aionowplaying import NowPlaying, LoopStatus

    player = NowPlaying(
        "My Player",
        on_play=lambda: player.play(),
        on_pause=lambda: player.pause(),
        on_next=lambda: player.next_track(),
        on_previous=lambda: player.previous_track(),
        on_stop=lambda: player.stop(),
        on_seek=lambda pos: player.seek(pos),  # pos is timedelta
        on_volume=lambda vol: player.set_volume(vol),  # vol is float 0.0-1.0
        on_shuffle=lambda enabled: player.set_shuffle(enabled),  # enabled is bool
        on_loop=lambda status: player.set_loop(status),  # status is LoopStatus
    )

Capabilities are automatically inferred from the callbacks you provide. For example,
if you provide ``on_play``, ``CanPlay`` will be set to ``True`` automatically.

Advanced Usage
--------------

For fine-grained control, inherit from ``BaseInterface``:

.. code-block:: python

    from aionowplaying import BaseInterface

    class MyPlayer(BaseInterface):
        async def on_play(self):
            # Custom implementation
            pass

        async def on_pause(self):
            # Custom implementation
            pass

.. note::

    The ``select_interface()`` function and ``NowPlayingInterface`` alias are deprecated.
    Use ``NowPlaying`` instead.