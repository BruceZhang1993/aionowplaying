# PROJECT KNOWLEDGE BASE

**Generated:** 2026-03-02
**Commit:** 481
**Branch:** main

## OVERVIEW

Cross-platform Python library for "Now Playing" media integration. Abstracts Linux MPRIS2, Windows SMTC, and macOS MediaPlayer behind unified async interface. Pydantic models for typed playback properties.

## STRUCTURE

```
aionowplaying/
├── src/aionowplaying/       # Main library (src-layout)
│   ├── __init__.py          # Public API exports
│   └── interface/           # Platform implementations
├── tests/                   # Pytest suite (platform-specific)
├── docs/                    # Sphinx documentation
└── .github/workflows/       # CI: Ubuntu/Windows/macOS × Python 3.10-3.14
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Add new platform | `src/aionowplaying/interface/` | Create new module, register in `__init__.py` |
| Extend data model | `interface/base.py` | `PlaybackProperties`, `PlayerProperties` |
| Public API changes | `__init__.py` | Update `__all__` list |
| Add test | `tests/test_*.py` | Platform-specific files, uses conftest.py fixtures |
| CI configuration | `.github/workflows/ci.yml` | Matrix: 3 platforms × 2 Python versions |

## CODE MAP

| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `select_interface` | Function | `interface/__init__.py:14` | Factory - returns platform-appropriate class |
| `BaseInterface` | Class | `interface/base.py:113` | Abstract base, callback handlers |
| `PlaybackProperties` | Model | `interface/base.py:77` | Pydantic model for playback state |
| `PropertyName` | Enum | `interface/base.py:11` | Player-level property names |
| `PlaybackPropertyName` | Enum | `interface/base.py:23` | Playback property names |
| `Mpris2Interface` | Class | `interface/mpris2.py:269` | Linux D-Bus MPRIS2 implementation |
| `WindowsInterface` | Class | `interface/windows.py:27` | Windows SMTC implementation |
| `MacOSInterface` | Class | `interface/macos.py:67` | macOS MediaPlayer implementation |

## CONVENTIONS

- **Async-first**: All callbacks (`on_play`, `on_pause`, etc.) are async
- **Pydantic models**: All data structures use Pydantic v2
- **src-layout**: Source in `src/aionowplaying/` (not root)
- **Platform isolation**: Each platform module imports dependencies conditionally in `pyproject.toml`
- **No CLI**: Library only, no `__main__.py` or console scripts

## ANTI-PATTERNS

- **Don't** import platform modules directly - use `select_interface()` factory
- **Don't** suppress `NotImplemented` from `select_interface()` - indicates unsupported platform
- **Don't** modify `PlaybackProperties` fields directly - use `set_playback_property()`

## UNIQUE STYLES

- **Callback pattern**: Override `on_*` methods in subclass to handle media controls
- **Property sync**: Set capability flags (`CanPlay`, `CanPause`) to enable/disable controls
- **Position units**: All time values in **microseconds**
- **Thread safety** (Windows): Callbacks may run in non-main thread; uses `asyncio.run_coroutine_threadsafe`

## COMMANDS

```bash
# Development
uv sync --dev                    # Install dev dependencies
uv run pytest -v                 # Run tests
uv run pytest -v --cov           # Run with coverage

# Build & Publish
uv build                         # Build sdist + wheel
uv publish                       # Publish to PyPI (needs UV_PUBLISH_TOKEN)

# Documentation
sphinx-build -b html docs docs/_build/html
```

## NOTES

- **D-Bus required** for Linux tests: `sudo apt install dbus-x11`
- **macOS tests** may exit 137 (allowed in CI)
- **Coverage omits** platform-specific modules not matching current OS (see `conftest.py`)
- **Release workflow**: Git tag → validates version match → builds → GitHub Release + PyPI