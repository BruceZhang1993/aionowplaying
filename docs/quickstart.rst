Quick Start
===========

This section will guide you through the basic usage of aionowplaying.

If you need URI support, start with the platform overview at
:doc:`platform-uri-activation`. That page explains the split between
"open a URI from the current process" and "receive URI activation from the
operating system", then links to the macOS and Windows host examples.

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

    # Wire media callbacks to your own application logic.
    def handle_play():
        pass

    def handle_pause():
        pass

    player = NowPlaying(
        "My Player",
        metadata={
            "title": "Song Name",
            "artist": ["Artist"],
            "album": "Album",
            "duration": timedelta(minutes=3, seconds=30),
        },
        on_play=handle_play,
        on_pause=handle_pause,
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

    def handle_play():
        pass

    def handle_pause():
        pass

    async def main():
        player = NowPlaying(
            "My Player",
            metadata={
                "title": "Song Name",
                "artist": ["Artist"],
                "duration": timedelta(minutes=3),
            },
            on_play=handle_play,
            on_pause=handle_pause,
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

    from aionowplaying import NowPlaying

    def handle_play():
        pass

    def handle_pause():
        pass

    player = NowPlaying(
        "My Player",
        on_play=handle_play,
        on_pause=handle_pause,
    )

Supported capability flags are derived from the callbacks the backend knows how to
surface. For example, providing ``on_play`` can enable the corresponding play
capability, but callback names are not universally or automatically mapped to
every possible capability.

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

URI Activation
--------------

``aionowplaying`` can help your current process open a URI, but it cannot
register a URL scheme or receive external URI activations by itself. Host
applications must define their own custom scheme, register it with the
operating system, and forward activated URIs back into player logic.

For the cross-platform overview and host-specific examples, see
:doc:`platform-uri-activation`.
