# NowPlaying Fluent API Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a simplified Fluent API for aionowplaying that reduces boilerplate and improves usability while maintaining backward compatibility.

**Architecture:** NowPlaying class wraps BaseInterface, providing property-based access, timedelta support, and automatic capability inference from callbacks.

**Tech Stack:** Python 3.10+, Pydantic, asyncio

---

## File Structure

| File | Action | Purpose |
|------|--------|---------|
| `src/aionowplaying/nowplaying.py` | Create | NowPlaying class implementation |
| `src/aionowplaying/__init__.py` | Modify | Export NowPlaying, add deprecation warnings |
| `src/aionowplaying/interface/__init__.py` | Modify | Deprecate select_interface |
| `tests/test_nowplaying.py` | Create | Unit tests for NowPlaying class |

---

## Chunk 1: Core NowPlaying Class Structure

### Task 1: Create NowPlaying class with initialization

**Files:**
- Create: `src/aionowplaying/nowplaying.py`
- Modify: `src/aionowplaying/interface/__init__.py`
- Modify: `src/aionowplaying/__init__.py`
- Test: `tests/test_nowplaying.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_nowplaying.py
import pytest
from aionowplaying import NowPlaying


def test_nowplaying_init_with_name():
    """Test basic initialization with just a name."""
    player = NowPlaying("Test Player")
    assert player is not None
    assert player.name == "Test Player"
    assert player._identity == "Test Player"


def test_nowplaying_init_with_identity():
    """Test initialization with custom identity."""
    player = NowPlaying("Test Player", identity="Custom Identity")
    assert player.name == "Test Player"
    assert player._identity == "Custom Identity"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_nowplaying.py::test_nowplaying_init_with_name tests/test_nowplaying.py::test_nowplaying_init_with_identity -v`
Expected: FAIL with "cannot import name 'NowPlaying'"

- [ ] **Step 3: Add _select_interface_impl to interface/__init__.py**

```python
# src/aionowplaying/interface/__init__.py (modify existing file)
import importlib
import sys
from typing import Type

from aionowplaying.interface.base import BaseInterface

INTERFACES_BY_SYSTEM = {
    'linux': 'aionowplaying.interface.mpris2.Mpris2Interface',
    'win32': 'aionowplaying.interface.windows.WindowsInterface',
    'darwin': 'aionowplaying.interface.macos.MacOSInterface',
}


def _select_interface_impl(system: str = None) -> Type[BaseInterface]:
    """Internal implementation of select_interface without deprecation warning."""
    if system is None:
        system = sys.platform
    name = INTERFACES_BY_SYSTEM.get(system, 'aionowplaying.interface.base.BaseInterface')
    mod = name.rsplit('.', 1)
    return getattr(importlib.import_module(mod[0]), mod[1])


def select_interface(system: str = None) -> Type[BaseInterface]:
    """Select the appropriate interface for the current platform."""
    return _select_interface_impl(system)
```

- [ ] **Step 4: Create NowPlaying class skeleton**

```python
# src/aionowplaying/nowplaying.py
from datetime import timedelta
from typing import Any, Callable

from aionowplaying.interface.base import (
    BaseInterface,
    LoopStatus,
    PlaybackProperties,
    PlaybackPropertyName,
    PlaybackStatus,
)
from aionowplaying.interface import _select_interface_impl
from aionowplaying.interface.base import PropertyName


class NowPlaying:
    """
    Simplified interface for Now Playing integration.

    Example:
        player = NowPlaying("My Player")
        player.title = "Song Name"
        player.artist = ["Artist"]
        await player.start()
    """

    def __init__(
        self,
        name: str,
        identity: str | None = None,
        metadata: dict[str, Any] | None = None,
        on_play: Callable[[], Any] | None = None,
        on_pause: Callable[[], Any] | None = None,
        on_next: Callable[[], Any] | None = None,
        on_previous: Callable[[], Any] | None = None,
        on_seek: Callable[[timedelta], Any] | None = None,
        on_stop: Callable[[], Any] | None = None,
        on_volume: Callable[[float], Any] | None = None,
        on_shuffle: Callable[[bool], Any] | None = None,
        on_loop: Callable[[LoopStatus], Any] | None = None,
    ):
        self.name = name
        self._identity = identity or name
        self._interface: BaseInterface = _select_interface_impl()(name)
        self._interface.set_property(PropertyName.Identity, self._identity)

        # Store callbacks
        self._callbacks: dict[str, Callable] = {
            'on_play': on_play,
            'on_pause': on_pause,
            'on_next': on_next,
            'on_previous': on_previous,
            'on_seek': on_seek,
            'on_stop': on_stop,
            'on_volume': on_volume,
            'on_shuffle': on_shuffle,
            'on_loop': on_loop,
        }

        # Setup capabilities based on callbacks
        self._setup_capabilities()

        # Apply initial metadata
        if metadata:
            self._apply_metadata(metadata)
```

- [ ] **Step 5: Add export to __init__.py**

```python
# src/aionowplaying/__init__.py
__all__ = ['NowPlaying', 'select_interface', 'BaseInterface', 'PropertyName', 'LoopStatus',
           'PlaybackPropertyName', 'PlaybackProperties', 'PlaybackStatus']

from aionowplaying.nowplaying import NowPlaying
from aionowplaying.interface import select_interface, BaseInterface
from aionowplaying.interface.base import PropertyName, LoopStatus, PlaybackPropertyName, PlaybackProperties, \
    PlaybackStatus
```

- [ ] **Step 6: Run test to verify it passes**

Run: `uv run pytest tests/test_nowplaying.py::test_nowplaying_init_with_name tests/test_nowplaying.py::test_nowplaying_init_with_identity -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add src/aionowplaying/nowplaying.py src/aionowplaying/__init__.py src/aionowplaying/interface/__init__.py tests/test_nowplaying.py
git commit -m "feat: add NowPlaying class with basic initialization"
```

---

### Task 2: Implement capability inference

**Files:**
- Modify: `src/aionowplaying/nowplaying.py`
- Test: `tests/test_nowplaying.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_nowplaying.py (add to existing file)
def test_capability_inference_from_callbacks():
    """Test that capabilities are auto-inferred from callbacks."""
    player = NowPlaying(
        "Test Player",
        on_play=lambda: None,
        on_pause=lambda: None,
        on_next=lambda: None,
    )

    # Check that capabilities were set
    assert player._interface.get_playback_property(PlaybackPropertyName.CanPlay) is True
    assert player._interface.get_playback_property(PlaybackPropertyName.CanPause) is True
    assert player._interface.get_playback_property(PlaybackPropertyName.CanGoNext) is True
    assert player._interface.get_playback_property(PlaybackPropertyName.CanControl) is True

    # Check that non-registered capabilities are False
    assert player._interface.get_playback_property(PlaybackPropertyName.CanGoPrevious) is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_nowplaying.py::test_capability_inference_from_callbacks -v`
Expected: FAIL with "AssertionError" or "AttributeError"

- [ ] **Step 3: Implement _setup_capabilities method**

```python
# src/aionowplaying/nowplaying.py (add method to NowPlaying class)
def _setup_capabilities(self):
    """Set playback capabilities based on registered callbacks."""
    control_callbacks = [
        'on_play', 'on_pause', 'on_next', 'on_previous',
        'on_seek', 'on_stop', 'on_volume', 'on_shuffle', 'on_loop'
    ]

    # Set CanControl if any control callback is registered
    has_control = any(self._callbacks.get(cb) for cb in control_callbacks)
    if has_control:
        self._interface.set_playback_property(PlaybackPropertyName.CanControl, True)

    # Set specific capabilities
    callback_capability_map = {
        'on_play': PlaybackPropertyName.CanPlay,
        'on_pause': PlaybackPropertyName.CanPause,
        'on_next': PlaybackPropertyName.CanGoNext,
        'on_previous': PlaybackPropertyName.CanGoPrevious,
        'on_seek': PlaybackPropertyName.CanSeek,
    }

    for callback_name, capability in callback_capability_map.items():
        if self._callbacks.get(callback_name):
            self._interface.set_playback_property(capability, True)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_nowplaying.py::test_capability_inference_from_callbacks -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/aionowplaying/nowplaying.py tests/test_nowplaying.py
git commit -m "feat: add automatic capability inference from callbacks"
```

---

### Task 3: Implement time conversion utilities

**Files:**
- Modify: `src/aionowplaying/nowplaying.py`
- Test: `tests/test_nowplaying.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_nowplaying.py (add to existing file)
from datetime import timedelta


def test_timedelta_to_microseconds():
    """Test timedelta to microseconds conversion."""
    player = NowPlaying("Test Player")

    # 1 second = 1,000,000 microseconds
    assert player._timedelta_to_microseconds(timedelta(seconds=1)) == 1_000_000

    # 1.5 seconds = 1,500,000 microseconds
    assert player._timedelta_to_microseconds(timedelta(seconds=1.5)) == 1_500_000

    # 3 minutes 30 seconds = 210,000,000 microseconds
    assert player._timedelta_to_microseconds(timedelta(minutes=3, seconds=30)) == 210_000_000


def test_microseconds_to_timedelta():
    """Test microseconds to timedelta conversion."""
    player = NowPlaying("Test Player")

    result = player._microseconds_to_timedelta(1_000_000)
    assert result == timedelta(seconds=1)

    result = player._microseconds_to_timedelta(210_000_000)
    assert result == timedelta(minutes=3, seconds=30)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_nowplaying.py::test_timedelta_to_microseconds tests/test_nowplaying.py::test_microseconds_to_timedelta -v`
Expected: FAIL with "AttributeError"

- [ ] **Step 3: Implement time conversion methods**

```python
# src/aionowplaying/nowplaying.py (add methods to NowPlaying class)
@staticmethod
def _timedelta_to_microseconds(td: timedelta) -> int:
    """Convert timedelta to microseconds."""
    return int(td.total_seconds() * 1_000_000)

@staticmethod
def _microseconds_to_timedelta(us: int) -> timedelta:
    """Convert microseconds to timedelta."""
    return timedelta(microseconds=us)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_nowplaying.py::test_timedelta_to_microseconds tests/test_nowplaying.py::test_microseconds_to_timedelta -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/aionowplaying/nowplaying.py tests/test_nowplaying.py
git commit -m "feat: add timedelta conversion utilities"
```

---

## Chunk 2: Metadata and Playback Properties

### Task 4: Implement metadata properties

**Files:**
- Modify: `src/aionowplaying/nowplaying.py`
- Test: `tests/test_nowplaying.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_nowplaying.py (add to existing file)
def test_title_property():
    """Test title property getter/setter."""
    player = NowPlaying("Test Player")
    player.title = "Test Song"
    assert player.title == "Test Song"


def test_artist_property():
    """Test artist property getter/setter."""
    player = NowPlaying("Test Player")

    # Test with list
    player.artist = ["Artist 1", "Artist 2"]
    assert player.artist == ["Artist 1", "Artist 2"]

    # Test with string (should convert to list)
    player.artist = "Single Artist"
    assert player.artist == ["Single Artist"]


def test_album_property():
    """Test album property getter/setter."""
    player = NowPlaying("Test Player")
    player.album = "Test Album"
    assert player.album == "Test Album"


def test_album_artist_property():
    """Test album_artist property getter/setter."""
    player = NowPlaying("Test Player")
    player.album_artist = ["Album Artist 1"]
    assert player.album_artist == ["Album Artist 1"]

    player.album_artist = "Single Album Artist"
    assert player.album_artist == ["Single Album Artist"]


def test_cover_property():
    """Test cover property getter/setter."""
    player = NowPlaying("Test Player")
    player.cover = "file:///path/to/cover.jpg"
    assert player.cover == "file:///path/to/cover.jpg"


def test_url_property():
    """Test url property getter/setter."""
    player = NowPlaying("Test Player")
    player.url = "file:///path/to/song.mp3"
    assert player.url == "file:///path/to/song.mp3"


def test_track_number_property():
    """Test track_number property getter/setter."""
    player = NowPlaying("Test Player")
    player.track_number = 5
    assert player.track_number == 5


def test_duration_property():
    """Test duration property with timedelta."""
    player = NowPlaying("Test Player")
    player.duration = timedelta(minutes=3, seconds=30)
    assert player.duration == timedelta(minutes=3, seconds=30)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_nowplaying.py::test_title_property tests/test_nowplaying.py::test_artist_property tests/test_nowplaying.py::test_album_property tests/test_nowplaying.py::test_album_artist_property tests/test_nowplaying.py::test_cover_property tests/test_nowplaying.py::test_url_property tests/test_nowplaying.py::test_track_number_property tests/test_nowplaying.py::test_duration_property -v`
Expected: FAIL with "AttributeError"

- [ ] **Step 3: Implement metadata properties**

```python
# src/aionowplaying/nowplaying.py (add properties to NowPlaying class)
@property
def title(self) -> str:
    return self._interface._playback_properties.Metadata.title

@title.setter
def title(self, value: str):
    self._interface._playback_properties.Metadata.title = value

@property
def artist(self) -> list[str]:
    return self._interface._playback_properties.Metadata.artist

@artist.setter
def artist(self, value: list[str] | str):
    if isinstance(value, str):
        value = [value]
    self._interface._playback_properties.Metadata.artist = value

@property
def album(self) -> str:
    return self._interface._playback_properties.Metadata.album

@album.setter
def album(self, value: str):
    self._interface._playback_properties.Metadata.album = value

@property
def album_artist(self) -> list[str]:
    return self._interface._playback_properties.Metadata.albumArtist

@album_artist.setter
def album_artist(self, value: list[str] | str):
    if isinstance(value, str):
        value = [value]
    self._interface._playback_properties.Metadata.albumArtist = value

@property
def cover(self) -> str:
    return self._interface._playback_properties.Metadata.cover

@cover.setter
def cover(self, value: str):
    self._interface._playback_properties.Metadata.cover = value

@property
def url(self) -> str:
    return self._interface._playback_properties.Metadata.url

@url.setter
def url(self, value: str):
    self._interface._playback_properties.Metadata.url = value

@property
def track_number(self) -> int:
    return self._interface._playback_properties.Metadata.trackNumber

@track_number.setter
def track_number(self, value: int):
    self._interface._playback_properties.Metadata.trackNumber = value

@property
def duration(self) -> timedelta | None:
    us = self._interface._playback_properties.Metadata.duration
    if us == 0:
        return None
    return self._microseconds_to_timedelta(us)

@duration.setter
def duration(self, value: timedelta):
    self._interface._playback_properties.Metadata.duration = self._timedelta_to_microseconds(value)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_nowplaying.py::test_title_property tests/test_nowplaying.py::test_artist_property tests/test_nowplaying.py::test_album_property tests/test_nowplaying.py::test_duration_property -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/aionowplaying/nowplaying.py tests/test_nowplaying.py
git commit -m "feat: add metadata properties (title, artist, album, duration, etc.)"
```

---

### Task 5: Implement playback state properties

**Files:**
- Modify: `src/aionowplaying/nowplaying.py`
- Test: `tests/test_nowplaying.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_nowplaying.py (add to existing file)
def test_position_property():
    """Test position property with timedelta."""
    player = NowPlaying("Test Player")
    player.position = timedelta(seconds=60)
    assert player.position == timedelta(seconds=60)


def test_is_playing_property():
    """Test is_playing property (read-only, use set_playing() to change)."""
    player = NowPlaying("Test Player")
    assert player.is_playing is False

    player.set_playing()
    assert player.is_playing is True
    assert player._interface.get_playback_property(PlaybackPropertyName.PlaybackStatus) == PlaybackStatus.Playing


def test_is_paused_property():
    """Test is_paused property (read-only, use set_paused() to change)."""
    player = NowPlaying("Test Player")

    player.set_paused()
    assert player.is_paused is True
    assert player._interface.get_playback_property(PlaybackPropertyName.PlaybackStatus) == PlaybackStatus.Paused


def test_is_stopped_property():
    """Test is_stopped property (read-only, use set_stopped() to change)."""
    player = NowPlaying("Test Player")

    player.set_stopped()
    assert player.is_stopped is True
    assert player._interface.get_playback_property(PlaybackPropertyName.PlaybackStatus) == PlaybackStatus.Stopped


def test_volume_property():
    """Test volume property."""
    player = NowPlaying("Test Player")
    player.volume = 0.5
    assert player.volume == 0.5


def test_shuffle_property():
    """Test shuffle property."""
    player = NowPlaying("Test Player")
    player.shuffle = True
    assert player.shuffle is True


def test_loop_status_property():
    """Test loop_status property."""
    player = NowPlaying("Test Player")
    player.loop_status = LoopStatus.Track
    assert player.loop_status == LoopStatus.Track


def test_rate_property():
    """Test rate property."""
    player = NowPlaying("Test Player")
    player.rate = 1.5
    assert player.rate == 1.5
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_nowplaying.py::test_position_property tests/test_nowplaying.py::test_is_playing_property tests/test_nowplaying.py::test_is_paused_property tests/test_nowplaying.py::test_is_stopped_property tests/test_nowplaying.py::test_volume_property tests/test_nowplaying.py::test_shuffle_property tests/test_nowplaying.py::test_loop_status_property tests/test_nowplaying.py::test_rate_property -v`
Expected: FAIL with "AttributeError"

- [ ] **Step 3: Implement playback state properties**

```python
# src/aionowplaying/nowplaying.py (add properties to NowPlaying class)
@property
def position(self) -> timedelta | None:
    us = self._interface._playback_properties.Position
    if us == 0:
        return None
    return self._microseconds_to_timedelta(us)

@position.setter
def position(self, value: timedelta):
    self._interface.set_playback_property(
        PlaybackPropertyName.Position,
        self._timedelta_to_microseconds(value)
    )

@property
def is_playing(self) -> bool:
    """Read-only property. Use set_playing() to change state."""
    return self._interface.get_playback_property(PlaybackPropertyName.PlaybackStatus) == PlaybackStatus.Playing

@property
def is_paused(self) -> bool:
    """Read-only property. Use set_paused() to change state."""
    return self._interface.get_playback_property(PlaybackPropertyName.PlaybackStatus) == PlaybackStatus.Paused

@property
def is_stopped(self) -> bool:
    """Read-only property. Use set_stopped() to change state."""
    return self._interface.get_playback_property(PlaybackPropertyName.PlaybackStatus) == PlaybackStatus.Stopped

@property
def volume(self) -> float:
    return self._interface.get_playback_property(PlaybackPropertyName.Volume)

@volume.setter
def volume(self, value: float):
    self._interface.set_playback_property(PlaybackPropertyName.Volume, value)

@property
def shuffle(self) -> bool:
    return self._interface.get_playback_property(PlaybackPropertyName.Shuffle)

@shuffle.setter
def shuffle(self, value: bool):
    self._interface.set_playback_property(PlaybackPropertyName.Shuffle, value)

@property
def loop_status(self) -> LoopStatus:
    return self._interface.get_playback_property(PlaybackPropertyName.LoopStatus)

@loop_status.setter
def loop_status(self, value: LoopStatus):
    self._interface.set_playback_property(PlaybackPropertyName.LoopStatus, value)

@property
def rate(self) -> float:
    return self._interface.get_playback_property(PlaybackPropertyName.Rate)

@rate.setter
def rate(self, value: float):
    self._interface.set_playback_property(PlaybackPropertyName.Rate, value)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_nowplaying.py::test_position_property tests/test_nowplaying.py::test_is_playing_property tests/test_nowplaying.py::test_is_paused_property tests/test_nowplaying.py::test_is_stopped_property tests/test_nowplaying.py::test_volume_property tests/test_nowplaying.py::test_shuffle_property tests/test_nowplaying.py::test_loop_status_property tests/test_nowplaying.py::test_rate_property -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/aionowplaying/nowplaying.py tests/test_nowplaying.py
git commit -m "feat: add playback state properties (position, is_playing, volume, shuffle, etc.)"
```

---

### Task 6: Implement state convenience methods and update()

**Files:**
- Modify: `src/aionowplaying/nowplaying.py`
- Test: `tests/test_nowplaying.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_nowplaying.py (add to existing file)
def test_set_playing_method():
    """Test set_playing() convenience method."""
    player = NowPlaying("Test Player")
    player.set_playing()
    assert player.is_playing is True


def test_set_paused_method():
    """Test set_paused() convenience method."""
    player = NowPlaying("Test Player")
    player.set_paused()
    assert player.is_paused is True


def test_set_stopped_method():
    """Test set_stopped() convenience method."""
    player = NowPlaying("Test Player")
    player.set_playing()
    player.set_stopped()
    assert player.is_stopped is True


def test_update_method():
    """Test update() batch update method."""
    player = NowPlaying("Test Player")
    player.update(
        title="New Song",
        artist=["New Artist"],
        album="New Album",
        duration=timedelta(minutes=4),
        position=timedelta(seconds=30),
    )

    assert player.title == "New Song"
    assert player.artist == ["New Artist"]
    assert player.album == "New Album"
    assert player.duration == timedelta(minutes=4)
    assert player.position == timedelta(seconds=30)


def test_update_method_invalid_property():
    """Test update() raises error for invalid property."""
    player = NowPlaying("Test Player")

    with pytest.raises(ValueError, match="Unknown property"):
        player.update(invalid_property="value")


def test_update_method_does_not_modify_internal_state():
    """Test update() does not allow modifying internal properties."""
    player = NowPlaying("Test Player")
    original_name = player.name

    # Attempting to modify internal properties should fail
    with pytest.raises(ValueError, match="Unknown property"):
        player.update(name="Hacked Name")

    assert player.name == original_name
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_nowplaying.py::test_set_playing_method tests/test_nowplaying.py::test_set_paused_method tests/test_nowplaying.py::test_set_stopped_method tests/test_nowplaying.py::test_update_method tests/test_nowplaying.py::test_update_method_invalid_property tests/test_nowplaying.py::test_update_method_does_not_modify_internal_state -v`
Expected: FAIL with "AttributeError"

- [ ] **Step 3: Implement convenience methods and update()**

```python
# src/aionowplaying/nowplaying.py (add methods to NowPlaying class)
def set_playing(self) -> None:
    """Set playback status to Playing."""
    self._interface.set_playback_property(PlaybackPropertyName.PlaybackStatus, PlaybackStatus.Playing)

def set_paused(self) -> None:
    """Set playback status to Paused."""
    self._interface.set_playback_property(PlaybackPropertyName.PlaybackStatus, PlaybackStatus.Paused)

def set_stopped(self) -> None:
    """Set playback status to Stopped."""
    self._interface.set_playback_property(PlaybackPropertyName.PlaybackStatus, PlaybackStatus.Stopped)

# Allowed properties for update()
_UPDATE_ALLOWED_PROPERTIES = frozenset({
    'title', 'artist', 'album', 'album_artist', 'cover', 'url',
    'track_number', 'duration', 'position', 'volume', 'shuffle',
    'loop_status', 'rate',
})

def update(self, **kwargs) -> None:
    """
    Batch update multiple properties.

    Supported kwargs:
    - Metadata: title, artist, album, album_artist, cover, url, track_number, duration
    - Playback: position, volume, shuffle, loop_status, rate

    Raises:
        ValueError: If an unknown property is provided.
    """
    for key in kwargs:
        if key not in self._UPDATE_ALLOWED_PROPERTIES:
            raise ValueError(f"Unknown property: {key}")

    for key, value in kwargs.items():
        setattr(self, key, value)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_nowplaying.py::test_set_playing_method tests/test_nowplaying.py::test_set_paused_method tests/test_nowplaying.py::test_set_stopped_method tests/test_nowplaying.py::test_update_method tests/test_nowplaying.py::test_update_method_invalid_property tests/test_nowplaying.py::test_update_method_does_not_modify_internal_state -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/aionowplaying/nowplaying.py tests/test_nowplaying.py
git commit -m "feat: add state convenience methods and batch update() with whitelist"
```

---

## Chunk 3: Metadata Initialization and Lifecycle

### Task 7: Implement metadata initialization

**Files:**
- Modify: `src/aionowplaying/nowplaying.py`
- Test: `tests/test_nowplaying.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_nowplaying.py (add to existing file)
def test_initial_metadata():
    """Test initialization with metadata dict."""
    player = NowPlaying(
        "Test Player",
        metadata={
            "title": "Initial Song",
            "artist": ["Initial Artist"],
            "album": "Initial Album",
            "duration": timedelta(minutes=3),
        }
    )

    assert player.title == "Initial Song"
    assert player.artist == ["Initial Artist"]
    assert player.album == "Initial Album"
    assert player.duration == timedelta(minutes=3)


def test_identity_parameter():
    """Test identity parameter defaults to name."""
    player1 = NowPlaying("Player Name")
    assert player1._identity == "Player Name"

    player2 = NowPlaying("Player Name", identity="Custom Identity")
    assert player2._identity == "Custom Identity"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_nowplaying.py::test_initial_metadata tests/test_nowplaying.py::test_identity_parameter -v`
Expected: FAIL

- [ ] **Step 3: Implement _apply_metadata method**

```python
# src/aionowplaying/nowplaying.py (add method to NowPlaying class)
def _apply_metadata(self, metadata: dict[str, Any]) -> None:
    """Apply initial metadata from dict."""
    # Map metadata keys to properties
    metadata_mapping = {
        'title': 'title',
        'artist': 'artist',
        'album': 'album',
        'album_artist': 'album_artist',
        'cover': 'cover',
        'url': 'url',
        'track_number': 'track_number',
        'duration': 'duration',
    }

    for key, prop in metadata_mapping.items():
        if key in metadata:
            setattr(self, prop, metadata[key])
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_nowplaying.py::test_initial_metadata tests/test_nowplaying.py::test_identity_parameter -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/aionowplaying/nowplaying.py tests/test_nowplaying.py
git commit -m "feat: add metadata initialization from dict"
```

---

### Task 8: Implement lifecycle methods (start/stop)

**Files:**
- Modify: `src/aionowplaying/nowplaying.py`
- Test: `tests/test_nowplaying.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_nowplaying.py (add to existing file)
import asyncio


@pytest.mark.asyncio
async def test_start_stop_lifecycle():
    """Test start and stop lifecycle methods."""
    player = NowPlaying("Test Player")

    # Start should call internal interface start
    # We can't easily test this without mocking, so just verify it doesn't raise
    try:
        await player.start()
    except Exception as e:
        # Some platforms may fail due to missing dependencies
        # but the method should exist
        pass

    await player.stop()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_nowplaying.py::test_start_stop_lifecycle -v`
Expected: FAIL with "AttributeError"

- [ ] **Step 3: Implement lifecycle methods**

```python
# src/aionowplaying/nowplaying.py (add methods to NowPlaying class)
async def start(self) -> None:
    """Start the Now Playing backend."""
    await self._interface.start()

async def stop(self) -> None:
    """Stop the Now Playing backend."""
    await self._interface.stop()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_nowplaying.py::test_start_stop_lifecycle -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/aionowplaying/nowplaying.py tests/test_nowplaying.py
git commit -m "feat: add start/stop lifecycle methods"
```

---

## Chunk 4: Callback Wrapper and Deprecation

### Task 9: Implement callback wrapper for BaseInterface

**Files:**
- Modify: `src/aionowplaying/nowplaying.py`
- Test: `tests/test_nowplaying.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_nowplaying.py (add to existing file)
import asyncio


@pytest.mark.asyncio
async def test_callback_execution():
    """Test that registered callbacks are executed."""
    call_log = []

    player = NowPlaying(
        "Test Player",
        on_play=lambda: call_log.append('play'),
        on_pause=lambda: call_log.append('pause'),
    )

    # Simulate callback execution through the interface
    await player._interface.on_play()
    await player._interface.on_pause()

    # Allow any async tasks to complete
    await asyncio.sleep(0.1)

    assert 'play' in call_log
    assert 'pause' in call_log
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_nowplaying.py::test_callback_execution -v`
Expected: FAIL - callbacks not connected to interface

- [ ] **Step 3: Implement _run_callback and _CallbackWrapper**

```python
# src/aionowplaying/nowplaying.py (add to NowPlaying class)
import asyncio

def _run_callback(self, name: str, *args) -> None:
    """Execute a callback, handling both sync and async."""
    callback = self._callbacks.get(name)
    if callback:
        result = callback(*args)
        if asyncio.iscoroutine(result):
            asyncio.create_task(result)
```

Now we need to create a wrapper that connects the interface callbacks to NowPlaying callbacks. Add this to the `__init__` method after `_setup_capabilities()`:

```python
# In __init__, after _setup_capabilities():
self._setup_callback_wrapper()
```

Add the wrapper setup method:

```python
# src/aionowplaying/nowplaying.py (add method to NowPlaying class)
def _setup_callback_wrapper(self) -> None:
    """Set up callback wrappers to connect interface to user callbacks."""
    # Override interface callbacks to call our callbacks
    original_on_play = self._interface.on_play
    original_on_pause = self._interface.on_pause
    original_on_next = self._interface.on_next
    original_on_previous = self._interface.on_previous
    original_on_seek = self._interface.on_seek
    original_on_stop = self._interface.on_stop
    original_on_volume = self._interface.on_volume
    original_on_shuffle = self._interface.on_shuffle
    original_on_loop = self._interface.on_loop_status

    async def wrapped_on_play():
        self._run_callback('on_play')

    async def wrapped_on_pause():
        self._run_callback('on_pause')

    async def wrapped_on_next():
        self._run_callback('on_next')

    async def wrapped_on_previous():
        self._run_callback('on_previous')

    async def wrapped_on_seek(offset: int):
        delta = self._microseconds_to_timedelta(offset)
        self._run_callback('on_seek', delta)

    async def wrapped_on_stop():
        self._run_callback('on_stop')

    async def wrapped_on_volume(volume: float):
        self._run_callback('on_volume', volume)

    async def wrapped_on_shuffle(shuffle: bool):
        self._run_callback('on_shuffle', shuffle)

    async def wrapped_on_loop(status):
        self._run_callback('on_loop', status)

    # Assign wrapped callbacks
    self._interface.on_play = wrapped_on_play
    self._interface.on_pause = wrapped_on_pause
    self._interface.on_next = wrapped_on_next
    self._interface.on_previous = wrapped_on_previous
    self._interface.on_seek = wrapped_on_seek
    self._interface.on_stop = wrapped_on_stop
    self._interface.on_volume = wrapped_on_volume
    self._interface.on_shuffle = wrapped_on_shuffle
    self._interface.on_loop_status = wrapped_on_loop
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_nowplaying.py::test_callback_execution -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/aionowplaying/nowplaying.py tests/test_nowplaying.py
git commit -m "feat: connect user callbacks to interface callbacks"
```

---

### Task 10: Add deprecation warnings to old API

**Files:**
- Modify: `src/aionowplaying/interface/__init__.py`
- Modify: `src/aionowplaying/__init__.py`
- Test: `tests/test_nowplaying.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_nowplaying.py (add to existing file)
import warnings


def test_select_interface_deprecation():
    """Test that select_interface shows deprecation warning."""
    from aionowplaying.interface import select_interface

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        select_interface()

        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "deprecated" in str(w[0].message).lower()


def test_nowplaying_interface_deprecation():
    """Test that NowPlayingInterface shows deprecation warning."""
    import aionowplaying

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        _ = aionowplaying.NowPlayingInterface

        assert len(w) >= 1
        assert any(issubclass(x.category, DeprecationWarning) for x in w)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_nowplaying.py::test_select_interface_deprecation tests/test_nowplaying.py::test_nowplaying_interface_deprecation -v`
Expected: FAIL - no warnings raised

- [ ] **Step 3: Implement deprecation warnings**

```python
# src/aionowplaying/interface/__init__.py
import importlib
import sys
import warnings
from typing import Type

from aionowplaying.interface.base import BaseInterface

INTERFACES_BY_SYSTEM = {
    'linux': 'aionowplaying.interface.mpris2.Mpris2Interface',
    'win32': 'aionowplaying.interface.windows.WindowsInterface',
    'darwin': 'aionowplaying.interface.macos.MacOSInterface',
}


def _select_interface_impl(system: str = None) -> Type[BaseInterface]:
    """Internal implementation of select_interface without warning."""
    if system is None:
        system = sys.platform
    name = INTERFACES_BY_SYSTEM.get(system, 'aionowplaying.interface.base.BaseInterface')
    mod = name.rsplit('.', 1)
    return getattr(importlib.import_module(mod[0]), mod[1])


def select_interface(system: str = None) -> Type[BaseInterface]:
    """
    Select the appropriate interface for the current platform.

    .. deprecated:: 0.12.0
        Use :class:`aionowplaying.NowPlaying` instead.
    """
    warnings.warn(
        "select_interface() is deprecated. Use aionowplaying.NowPlaying instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return _select_interface_impl(system)
```

```python
# src/aionowplaying/__init__.py
__all__ = ['NowPlaying', 'select_interface', 'BaseInterface', 'PropertyName', 'LoopStatus',
           'PlaybackPropertyName', 'PlaybackProperties', 'PlaybackStatus', 'NowPlayingInterface']

import warnings
from typing import Type

from aionowplaying.nowplaying import NowPlaying
from aionowplaying.interface import select_interface, BaseInterface
from aionowplaying.interface.base import PropertyName, LoopStatus, PlaybackPropertyName, PlaybackProperties, \
    PlaybackStatus


def __getattr__(name: str):
    """Provide deprecated access to NowPlayingInterface."""
    if name == "NowPlayingInterface":
        warnings.warn(
            "NowPlayingInterface is deprecated. Use NowPlaying instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return select_interface()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# Keep for backward compatibility (will be removed in v1.0.0)
NowPlayingInterface: Type[BaseInterface] = None  # type: ignore
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_nowplaying.py::test_select_interface_deprecation tests/test_nowplaying.py::test_nowplaying_interface_deprecation -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/aionowplaying/interface/__init__.py src/aionowplaying/__init__.py tests/test_nowplaying.py
git commit -m "feat: add deprecation warnings to select_interface and NowPlayingInterface"
```

---

## Chunk 5: Documentation and Final Polish

### Task 11: Update README.md

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update Quick Start section**

Replace the Quick Start section in README.md:

```markdown
## Quick Start

```python
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
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: update README with new NowPlaying API"
```

---

### Task 12: Run full test suite

- [ ] **Step 1: Run all tests**

Run: `uv run pytest -v`
Expected: All tests PASS

- [ ] **Step 2: Run tests with coverage**

Run: `uv run pytest -v --cov`
Expected: Coverage report shows NowPlaying class coverage

- [ ] **Step 3: Fix any failures**

If any tests fail, fix them and re-run.

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "chore: final cleanup and test verification"
```

---

## Summary

This plan creates:

1. **NowPlaying class** - Simplified fluent API for the library
2. **Automatic capability inference** - Callbacks enable capabilities automatically
3. **timedelta support** - Time values use Python's timedelta instead of microseconds
4. **Property-based access** - Direct property assignment instead of enum-heavy setters
5. **Batch updates** - `update()` method for efficient multi-property updates
6. **Deprecation warnings** - Old API still works but warns users to migrate

All changes maintain backward compatibility with the existing `BaseInterface` and `select_interface()` API.