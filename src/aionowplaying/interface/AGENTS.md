# Interface Module

Platform abstraction layer for Now Playing integration.

## OVERVIEW

Strategy pattern implementation - `BaseInterface` defines contract, platform modules implement specifics, `select_interface()` auto-selects at runtime.

## STRUCTURE

```
interface/
├── __init__.py    # select_interface() factory
├── base.py        # BaseInterface, enums, Pydantic models
├── mpris2.py      # Linux MPRIS2 (D-Bus)
├── windows.py     # Windows SMTC
└── macos.py       # macOS MediaPlayer
```

## WHERE TO LOOK

| Task | File | Location |
|------|------|----------|
| Add new property | `base.py` | `PropertyName` or `PlaybackPropertyName` enum + model field |
| Add new callback | `base.py` | `BaseInterface.on_*` method |
| New platform | New module | Register in `__init__.py` `INTERFACES_BY_SYSTEM` |
| D-Bus signal | `mpris2.py` | `MprisPlayerServiceInterface` methods |
| SMTC mapping | `windows.py` | `set_playback_property()` branches |
| macOS commands | `macos.py` | `_handle_change_*` methods |

## CONVENTIONS

- **Override `on_*` methods** in subclass to respond to media controls
- **Call `set_*_property()`** to update state and emit notifications
- **Position/Duration** in microseconds everywhere
- **Capability flags** must be set to enable controls (`CanPlay`, `CanSeek`, etc.)

## ANTI-PATTERNS

- **Don't** access `_properties` directly - use getters/setters
- **Don't** forget to call `super().set_playback_property()` for unhandled properties
- **Don't** block in `on_*` callbacks - they must be async

## PLATFORM NOTES

### Linux (mpris2.py)
- Uses `dbus-fast` for async D-Bus
- Exports `org.mpris.MediaPlayer2` interfaces
- Bus name: `org.mpris.MediaPlayer2.{name}`
- `seeked()` emits `Seeked` signal
- Ignore LSP errors caused by DBus type signatures, eg. Error [57:35] "s" is not defined

### Windows (windows.py)
- Uses `winrt` Windows Runtime projections
- `MediaPlayer.command_manager.is_enabled = False` for manual SMTC control
- Callbacks may run in non-main thread → `_run_task()` handles dispatch
- No volume setter (SMTC exposes `SoundLevel` read-only)

### macOS (macos.py)
- Uses `pyobjc-framework-MediaPlayer`
- `MPNowPlayingInfoCenter` + `MPRemoteCommandCenter`
- Must update position on status change (macOS bug workaround)
- Some properties read-only depending on OS/framework version
