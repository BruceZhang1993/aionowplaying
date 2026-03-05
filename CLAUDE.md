# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Cross-platform Python library for "Now Playing" media integration. Abstracts Linux MPRIS2, Windows SMTC, and macOS MediaPlayer behind a unified async interface using Pydantic models.

## Commands

```bash
# Development
uv sync --dev                    # Install dev dependencies
uv run pytest -v                 # Run all tests
uv run pytest -v --cov           # Run tests with coverage
uv run pytest -v tests/test_base_interface.py  # Run single test file

# Build & Publish
uv build                         # Build sdist + wheel
uv publish                       # Publish to PyPI (needs UV_PUBLISH_TOKEN)

# Documentation
sphinx-build -b html docs docs/_build/html
```

## Architecture

**src-layout**: Source code in `src/aionowplaying/` (not root).

**Strategy Pattern**: `BaseInterface` (abstract base) → platform implementations selected by `select_interface()`:

| Platform | Module | Implementation |
|----------|--------|----------------|
| Linux | `interface/mpris2.py` | D-Bus MPRIS2 via `dbus-fast` |
| Windows | `interface/windows.py` | SMTC via `winrt` |
| macOS | `interface/macos.py` | MediaPlayer via `pyobjc` |

**Key Classes**:
- `BaseInterface` (`interface/base.py:113`) - Abstract base with callback handlers
- `PlaybackProperties` (`interface/base.py:77`) - Pydantic model for playback state
- `PlaybackProperties.MetadataBean` (`interface/base.py:78`) - Track metadata model
- `PropertyName` / `PlaybackPropertyName` - Enums for property names

## Usage Pattern

```python
import asyncio
import aionowplaying as aionp

# Factory pattern - auto-selects platform implementation
backend = aionp.select_interface()("My Player")

# Set properties
backend.set_property(aionp.PropertyName.Identity, "My Player")
backend.set_playback_property(aionp.PlaybackPropertyName.PlaybackStatus, aionp.PlaybackStatus.Playing)

# Start backend (blocking)
asyncio.run(backend.start())

# Or run in background
asyncio.ensure_future(backend.start())
```

## Conventions

- **Async-first**: All callbacks (`on_play`, `on_pause`, `on_next`, etc.) are async
- **Position/Duration**: All time values in **microseconds**
- **Property access**: Use `set_playback_property()` / `get_playback_property()`, not direct field access
- **Capability flags**: Set `CanPlay`, `CanPause`, `CanSeek`, `CanGoNext`, etc. to `True` to enable controls
- **Callback override**: Subclass `BaseInterface` and override `on_*` methods to handle media controls

## Platform-Specific Notes

### Linux (mpris2.py)
- CI tests require dbus-x11: `sudo apt install dbus-x11` (normal desktop environments already have D-Bus)
- CI tests run with `dbus-launch --exit-with-session`
- Bus name: `org.mpris.MediaPlayer2.{name}`
- **LSP warning**: Ignore "s" is not defined errors - DBus type signatures (`'s'`, `'x'`, `'b'`, etc.) confuse LSP

### Windows (windows.py)
- Callbacks may run in non-main thread → `_run_task()` uses `asyncio.run_coroutine_threadsafe`
- SMTC exposes `SoundLevel` read-only → no volume setter
- Timeline properties must be set for seek functionality

### macOS (macos.py)
- Tests may exit 137 in CI (allowed)
- Must update position on status change (macOS bug workaround)
- Some properties read-only depending on OS/framework version
- Artwork only loads from local files (remote URLs may block)

## Test Structure

Tests are platform-specific with skip markers:

```python
pytestmark = pytest.mark.skipif(sys.platform != "linux", reason="Linux-only tests")
```

- `test_base_interface.py` - Cross-platform base tests
- `test_interface_select.py` - Factory selection tests
- `test_mpris2_interface.py` - Linux MPRIS2 tests
- `test_windows_interface.py` - Windows SMTC tests
- `test_macos_interface.py` - macOS MediaPlayer tests

## CI/CD

- **Matrix**: Ubuntu/Windows/macOS × Python 3.10-3.14
- **Coverage**: Uploaded to Codecov
- **Release**: Git tag (e.g., `v0.11.3`) → validates version match → builds → GitHub Release + PyPI

## Common Patterns

### Adding a new property
1. Add enum value to `PropertyName` or `PlaybackPropertyName` in `base.py`
2. Add field to `PlayerProperties` or `PlaybackProperties` model
3. Implement mapping in each platform's `set_playback_property()` method
4. Update `__all__` in `__init__.py` if exposing publicly

### Adding a new callback
1. Add async method `on_xxx()` to `BaseInterface` in `base.py`
2. Call it from platform-specific event handler
3. Add test in appropriate `test_*_interface.py`

### Adding a new platform
1. Create new module in `interface/` directory
2. Subclass `BaseInterface` and implement required methods
3. Register in `INTERFACES_BY_SYSTEM` dict in `interface/__init__.py`
4. Add platform-specific dependencies to `pyproject.toml` with `sys_platform` marker