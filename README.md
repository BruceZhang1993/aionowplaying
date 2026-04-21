# aionowplaying

[English](README.md) | [中文](README.zh-CN.md)

[![CI](https://github.com/BruceZhang1993/aionowplaying/actions/workflows/ci.yml/badge.svg)](https://github.com/BruceZhang1993/aionowplaying/actions/workflows/ci.yml)
[![codecov](https://codecov.io/github/BruceZhang1993/aionowplaying/graph/badge.svg?token=RQ93AOUTDC)](https://codecov.io/github/BruceZhang1993/aionowplaying)
[![PyPI version](https://img.shields.io/pypi/v/aionowplaying.svg)](https://pypi.org/project/aionowplaying/)
[![Python versions](https://img.shields.io/pypi/pyversions/aionowplaying.svg)](https://pypi.org/project/aionowplaying/)
[![PyPI downloads](https://img.shields.io/pypi/dm/aionowplaying.svg)](https://pypi.org/project/aionowplaying/)
[![Platforms](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-4c1.svg)](https://pypi.org/project/aionowplaying/)
[![Read the Docs](https://readthedocs.org/projects/aionowplaying/badge/?version=latest)](https://aionowplaying.readthedocs.io/en/latest/)
[![Made with uv](https://img.shields.io/badge/made%20with-uv-6e56cf?logo=uv&logoColor=white)](https://docs.astral.sh/uv/)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE.txt)

A cross-platform Now Playing client for Linux (MPRIS2), macOS, and Windows.

## Features

- Unified Python interface for Now Playing integration across platforms.
- Platform-specific backends selected automatically at runtime.
- Typed playback/property models powered by Pydantic.

## Installation

```shell
pip install aionowplaying
```

If you use `uv`:

```shell
uv add aionowplaying
```

## Quick Start

```python
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
```

### Advanced Usage

For fine-grained control, inherit from `BaseInterface`:

```python
from aionowplaying import BaseInterface

class MyPlayer(BaseInterface):
    async def on_play(self):
        # Custom implementation
        pass

    async def on_pause(self):
        # Custom implementation
        pass
```

## BaseInterface Platform Coverage

The tables below describe native backend coverage for each `BaseInterface` method. They focus on platform mapping, not just whether the method can be overridden in Python.

- `🟢 Native`: implemented or triggered by the platform backend.
- `🟡 Partial`: available with limitations or semantics that differ from the base method contract.
- `⚪ Cache only`: stored locally, but not exposed by the native platform API.
- `🔴 Unimplemented`: no platform-specific implementation. Base no-op methods are treated as unimplemented.

### Construction And Lifecycle

| Method | Linux (MPRIS2) | macOS | Windows |
| --- | --- | --- | --- |
| `__init__` | 🟢 Native<br>D-Bus setup | 🟢 Native<br>MediaPlayer center setup | 🟢 Native<br>SMTC setup |
| `start` | 🟢 Native<br>D-Bus connect/export loop | 🟢 Native<br>no-op | 🟢 Native<br>no-op |
| `stop` | 🟢 Native<br>D-Bus disconnect | 🔴 Unimplemented | 🟡 Partial<br>local flag only |

### App-Level Callbacks

| Method | Linux (MPRIS2) | macOS | Windows |
| --- | --- | --- | --- |
| `on_fullscreen` | 🟢 Native<br>`Fullscreen` setter | 🔴 Unimplemented | 🔴 Unimplemented |
| `on_raise` | 🟢 Native<br>`Raise` command | 🔴 Unimplemented | 🔴 Unimplemented |
| `on_quit` | 🟢 Native<br>`Quit` command | 🔴 Unimplemented | 🔴 Unimplemented |

### Playback Callbacks

| Method | Linux (MPRIS2) | macOS | Windows |
| --- | --- | --- | --- |
| `on_loop_status` | 🟢 Native<br>`LoopStatus` setter | 🟢 Native<br>repeat command | 🟢 Native<br>repeat request |
| `on_rate` | 🟢 Native<br>`Rate` setter | 🟢 Native<br>rate command | 🟢 Native<br>rate request |
| `on_shuffle` | 🟢 Native<br>`Shuffle` setter | 🟢 Native<br>shuffle command | 🟢 Native<br>shuffle request |
| `on_volume` | 🟢 Native<br>`Volume` setter | 🔴 Unimplemented | 🟡 Partial<br>read-only sound level |
| `on_next` | 🟢 Native<br>`Next` command | 🟢 Native<br>next command | 🟢 Native<br>Next button |
| `on_previous` | 🟢 Native<br>`Previous` command | 🟢 Native<br>previous command | 🟢 Native<br>Previous button |
| `on_pause` | 🟢 Native<br>`Pause` command | 🟢 Native<br>pause command | 🟢 Native<br>Pause button |
| `on_play_pause` | 🟢 Native<br>`PlayPause` command | 🟢 Native<br>toggle command | 🔴 Unimplemented |
| `on_play` | 🟢 Native<br>`Play` command | 🟢 Native<br>play command | 🟢 Native<br>Play button |
| `on_stop` | 🟢 Native<br>`Stop` command | 🟡 Partial<br>framework-dependent | 🟢 Native<br>Stop button |

### Position And URI Callbacks

| Method | Linux (MPRIS2) | macOS | Windows |
| --- | --- | --- | --- |
| `on_seek` | 🟢 Native<br>offset seek | 🟡 Partial<br>absolute position | 🟡 Partial<br>absolute position |
| `on_open_uri` | 🟢 Native<br>`OpenUri` command | 🟡 Library helper<br>open URI from current process | 🟡 Library helper<br>open URI from current process |
| `on_set_position` | 🟢 Native<br>`SetPosition` command | 🟢 Native<br>position command | 🟢 Native<br>position request |
| `seeked` | 🟢 Native<br>`Seeked` signal | 🔴 Unimplemented | 🔴 Unimplemented |

### URI Activation

URI activation is a split responsibility:

- On Linux, `on_open_uri` is exposed natively through MPRIS.
- On macOS and Windows, the library can help the current process open a URI.
- Registering a custom protocol and receiving system URI activation still belongs to the host application.

The scheme name is host-defined. `aionowplaying` does not require the public scheme to be `aionowplaying`.

Platform docs:

- [`docs/platform-uri-activation.rst`](docs/platform-uri-activation.rst)
- [`docs/platform-uri-activation-macos.rst`](docs/platform-uri-activation-macos.rst)
- [`docs/platform-uri-activation-windows.rst`](docs/platform-uri-activation-windows.rst)

### Property APIs

| Method | Linux (MPRIS2) | macOS | Windows |
| --- | --- | --- | --- |
| `set_property` | 🟢 Native<br>player properties | ⚪ Cache only<br>no player-level API | ⚪ Cache only<br>no player-level API |
| `set_playback_property` | 🟢 Native<br>playback properties | 🟡 Partial<br>some fields unsupported | 🟡 Partial<br>some fields local only |
| `set_tracklist_property` | 🟢 Native<br>writes MPRIS TrackList properties | ⚪ Cache only | ⚪ Cache only |
| `get_property` | 🟢 Native<br>player properties | ⚪ Cache only<br>cached value | ⚪ Cache only<br>cached value |
| `get_playback_property` | 🟢 Native<br>playback properties | 🟡 Partial<br>`Position`/`Rate` native, others cached | ⚪ Cache only<br>cached value |
| `get_tracklist_property` | 🟢 Native<br>TrackList properties | ⚪ Cache only<br>cached value | ⚪ Cache only<br>cached value |

## Documentation

- Interface/API documentation: https://aionowplaying.readthedocs.io/en/latest/
- API reference page: https://aionowplaying.readthedocs.io/en/latest/api.html

Build docs locally:

```shell
sphinx-build -b html docs docs/_build/html
```

## Development

Install dependencies and run tests:

```shell
uv sync --dev
uv run pytest -v
```

## Website

This repository also includes the project website and GitHub Pages build.

Install the development and docs dependencies first, then build the site locally:

```shell
uv sync --dev
uv pip install -r docs/requirements.txt
uv run python scripts/build_site.py
```

The generated site is written to `dist/`.

GitHub Pages is configured in [.github/workflows/pages.yml](.github/workflows/pages.yml) and publishes the site automatically on pushes to `master`.

## License

This project is licensed under GPL-3.0-only. See [LICENSE.txt](LICENSE.txt).

## Contributing

Contributions are welcome! Please follow the guidelines below.

### Reporting Issues

If you find a bug or have a feature request:

1. Search existing issues to avoid duplicates
2. Use the appropriate issue template:
   - **Bug Report**: For reporting bugs and errors
   - **Feature Request**: For suggesting new features
   - **Question/Other**: For other inquiries
3. Provide as much detail as possible:
   - For bugs: steps to reproduce, expected vs actual behavior, environment details
   - For features: use case and why it would be helpful

### Pull Requests

1. Fork the repository and create a feature branch from `master`
2. Run tests locally: `uv run pytest -v`
3. Ensure code follows project conventions
4. Write clear commit messages
5. Push your changes and create a pull request
6. Fill out the PR template with all relevant details

### Development Setup

```shell
# Clone your fork
git clone https://github.com/YOUR_USERNAME/aionowplaying.git
cd aionowplaying

# Install dependencies
uv sync --dev

# Run tests
uv run pytest -v

# Run linting (if available)
uv run ruff check .
```
