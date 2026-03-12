# NowPlaying Fluent API 设计文档

**日期**: 2026-03-12
**作者**: Claude + Bruce
**状态**: 草案

## 背景

当前 `aionowplaying` 库使用门槛较高，存在以下痛点：

1. **初始化繁琐** — `select_interface()("name")` 需要两步
2. **属性设置繁琐** — 逐个用枚举调用 `set_playback_property()`
3. **Metadata 更新频繁** — 缺少简洁的批量设置方式
4. **回调需要继承子类** — 简单回调也要定义子类
5. **时间单位转换** — 播放器常用秒/毫秒，库用微秒
6. **能力标记分散** — `CanPlay`、`CanPause` 等需要逐个设置

## 目标

设计简洁的 Fluent API，降低使用门槛，同时保持向后兼容。

## 设计

### 新入口类 `NowPlaying`

```python
from datetime import timedelta
from aionowplaying import NowPlaying

# 创建实例（自动选择平台）
player = NowPlaying(
    name="My Player",
    identity="My Music Player",           # 可选，默认同 name
    metadata={
        "title": "Song Name",
        "artist": ["Artist Name"],
        "album": "Album Name",
        "album_artist": ["Album Artist"],
        "cover": "file:///path/to/cover.jpg",
        "duration": timedelta(minutes=3, seconds=30),
        "track_number": 1,
        "url": "file:///path/to/song.mp3",
    },
    on_play=lambda: my_player.play(),
    on_pause=lambda: my_player.pause(),
    on_next=lambda: my_player.next(),
    on_previous=lambda: my_player.prev(),
    on_seek=lambda offset: my_player.seek_relative(offset),  # offset 是 timedelta，相对偏移（正数前进，负数后退）
    on_stop=lambda: my_player.stop(),
)
```

### 运行时更新 API

**属性赋值方式：**

```python
player.title = "New Song"
player.artist = ["New Artist"]
player.position = timedelta(seconds=60)
player.is_playing = True  # 布尔属性，设置播放状态
```

**批量更新方式：**

```python
player.update(
    title="New Song",
    artist=["New Artist"],
    album="New Album",
    position=timedelta(seconds=30),
    is_playing=True,
)
```

**播放状态便捷方法：**

```python
player.set_playing()    # 设置状态为 Playing
player.set_paused()     # 设置状态为 Paused
player.set_stopped()    # 设置状态为 Stopped
```

### 时间单位

使用 `datetime.timedelta` 表示时间，内部自动转换为微秒：

```python
player.duration = timedelta(minutes=3, seconds=30)  # 3:30
player.position = timedelta(seconds=45)
```

**回调中的时间参数**：`on_seek` 回调接收 `timedelta` 类型，内部自动处理转换。

### 能力自动推断

注册回调即自动启用对应能力：

| 回调 | 能力 |
|------|------|
| `on_play` | `CanPlay=True` |
| `on_pause` | `CanPause=True` |
| `on_next` | `CanGoNext=True` |
| `on_previous` | `CanGoPrevious=True` |
| `on_seek` | `CanSeek=True` |
| `on_stop` | `CanControl=True` |

**关于 `on_stop` 与 `CanControl`**：MPRIS 规范中 `CanControl` 是总开关。当注册 `on_stop` 时，设置 `CanControl=True`，这是当前实现的简化处理。后续可考虑增加 `on_quit` 等回调进一步细化。

### 回调支持范围

**支持的回调**（注册即启用能力）：

| 回调 | 签名 | 说明 |
|------|------|------|
| `on_play` | `Callable[[], Any]` | 播放 |
| `on_pause` | `Callable[[], Any]` | 暂停 |
| `on_next` | `Callable[[], Any]` | 下一曲 |
| `on_previous` | `Callable[[], Any]` | 上一曲 |
| `on_seek` | `Callable[[timedelta], Any]` | 相对跳转（正数前进，负数后退） |
| `on_stop` | `Callable[[], Any]` | 停止 |
| `on_volume` | `Callable[[float], Any]` | 音量变更（0.0-1.0） |
| `on_shuffle` | `Callable[[bool], Any]` | 随机播放切换 |
| `on_loop` | `Callable[[LoopStatus], Any]` | 循环模式变更 |

**暂不支持的回调**（高级功能，保留给 `BaseInterface` 继承使用）：

| 回调 | 说明 |
|------|------|
| `on_play_pause` | 可通过分别注册 `on_play` 和 `on_pause` 实现 |
| `on_fullscreen` | 全屏切换，播放器场景较少使用 |
| `on_raise` | 窗口置顶 |
| `on_quit` | 退出请求 |
| `on_rate` | 播放速率变更 |
| `on_open_uri` | 打开 URI |
| `on_set_position` | 设置绝对位置（与 `on_seek` 类似） |

### 同步与异步回调

`NowPlaying` **同时支持同步和异步回调**：

```python
# 同步回调
on_play=lambda: my_player.play()

# 异步回调
async def handle_play():
    await my_player.async_play()
on_play=handle_play
```

内部实现会检测回调类型，异步回调使用 `await`，同步回调直接调用。

### 模块结构

```
src/aionowplaying/
├── __init__.py          # 导出 NowPlaying
├── nowplaying.py        # 新增：NowPlaying 类
└── interface/
    ├── __init__.py      # select_interface 保留但弃用
    ├── base.py          # BaseInterface 保留
    ├── mpris2.py
    ├── windows.py
    └── macos.py
```

### 导出变更

```python
# 新增
NowPlaying

# 保留（但弃用）
select_interface
PropertyName
PlaybackPropertyName
NowPlayingInterface  # 原有别名，弃用

# 保留（不弃用）
BaseInterface      # 高级用户可继承
PlaybackStatus     # 枚举
LoopStatus         # 枚举
PlaybackProperties # Pydantic 模型
```

## 实现细节

### `NowPlaying` 类

```python
from datetime import timedelta
from typing import Any, Callable, Union
from aionowplaying.interface.base import LoopStatus

class NowPlaying:
    def __init__(
        self,
        name: str,
        identity: str | None = None,
        metadata: dict[str, Any] | None = None,
        # 播放控制回调
        on_play: Callable[[], Any] | None = None,
        on_pause: Callable[[], Any] | None = None,
        on_next: Callable[[], Any] | None = None,
        on_previous: Callable[[], Any] | None = None,
        on_seek: Callable[[timedelta], Any] | None = None,
        on_stop: Callable[[], Any] | None = None,
        # 其他控制回调
        on_volume: Callable[[float], Any] | None = None,
        on_shuffle: Callable[[bool], Any] | None = None,
        on_loop: Callable[[LoopStatus], Any] | None = None,
    ): ...

    # ========== 元数据属性 ==========
    @property
    def title(self) -> str: ...
    @title.setter
    def title(self, value: str): ...

    @property
    def artist(self) -> list[str]: ...
    @artist.setter
    def artist(self, value: list[str] | str): ...

    @property
    def album(self) -> str: ...
    @album.setter
    def album(self, value: str): ...

    @property
    def album_artist(self) -> list[str]: ...
    @album_artist.setter
    def album_artist(self, value: list[str] | str): ...

    @property
    def cover(self) -> str: ...
    @cover.setter
    def cover(self, value: str): ...

    @property
    def url(self) -> str: ...
    @url.setter
    def url(self, value: str): ...

    @property
    def track_number(self) -> int: ...
    @track_number.setter
    def track_number(self, value: int): ...

    @property
    def duration(self) -> timedelta | None: ...
    @duration.setter
    def duration(self, value: timedelta): ...

    # ========== 播放状态属性 ==========
    @property
    def position(self) -> timedelta | None: ...
    @position.setter
    def position(self, value: timedelta): ...

    @property
    def is_playing(self) -> bool: ...
    @is_playing.setter
    def is_playing(self, value: bool): ...

    @property
    def is_paused(self) -> bool: ...
    @is_paused.setter
    def is_paused(self, value: bool): ...

    @property
    def is_stopped(self) -> bool: ...
    @is_stopped.setter
    def is_stopped(self, value: bool): ...

    @property
    def volume(self) -> float: ...
    @volume.setter
    def volume(self, value: float): ...

    @property
    def shuffle(self) -> bool: ...
    @shuffle.setter
    def shuffle(self, value: bool): ...

    @property
    def loop_status(self) -> LoopStatus: ...
    @loop_status.setter
    def loop_status(self, value: LoopStatus): ...

    @property
    def rate(self) -> float: ...
    @rate.setter
    def rate(self, value: float): ...

    # ========== 批量更新 ==========
    def update(self, **kwargs) -> None:
        """
        批量更新属性。

        支持的参数：
        - 元数据：title, artist, album, album_artist, cover, url, track_number, duration
        - 播放状态：position, is_playing, is_paused, is_stopped
        - 其他：volume, shuffle, loop_status, rate
        """
        ...

    # ========== 播放状态便捷方法 ==========
    def set_playing(self) -> None: ...
    def set_paused(self) -> None: ...
    def set_stopped(self) -> None: ...

    # ========== 生命周期 ==========
    async def start(self) -> None: ...
    async def stop(self) -> None: ...
```

### 内部实现

`NowPlaying` 内部持有 `BaseInterface` 子类实例，代理所有调用：

```python
class NowPlaying:
    def __init__(self, name: str, ...):
        # 创建内部接口实例
        self._interface = _select_interface_impl()(name)
        self._callbacks: dict[str, Callable] = {}
        self._setup_callbacks(metadata)

    def _setup_callbacks(self, metadata: dict | None):
        # 设置元数据
        if metadata:
            self._apply_metadata(metadata)

        # 注册回调并设置能力
        if self._callbacks.get('on_play'):
            self._interface.set_playback_property(
                PlaybackPropertyName.CanPlay, True
            )
        # ... 其他回调类似

    def _run_callback(self, name: str, *args):
        """运行回调，自动处理同步/异步"""
        callback = self._callbacks.get(name)
        if callback:
            result = callback(*args)
            if asyncio.iscoroutine(result):
                asyncio.create_task(result)

    def _timedelta_to_microseconds(self, td: timedelta) -> int:
        """timedelta 转微秒"""
        return int(td.total_seconds() * 1_000_000)

    def _microseconds_to_timedelta(self, us: int) -> timedelta:
        """微秒转 timedelta"""
        return timedelta(microseconds=us)
```

### 回调包装器

为了支持 `BaseInterface` 的异步回调，需要创建包装类：

```python
class _CallbackWrapper(BaseInterface):
    def __init__(self, name: str, nowplaying: NowPlaying):
        super().__init__(name)
        self._nowplaying = nowplaying

    async def on_play(self):
        self._nowplaying._run_callback('on_play')

    async def on_pause(self):
        self._nowplaying._run_callback('on_pause')

    async def on_seek(self, offset: int):
        # offset 是微秒（相对偏移），转换为 timedelta
        delta = self._nowplaying._microseconds_to_timedelta(offset)
        self._nowplaying._run_callback('on_seek', delta)

    # ... 其他回调类似
```

## 弃用计划

| 版本 | 行为 |
|------|------|
| v0.12.0 | 新 API 发布，旧 API 触发 `DeprecationWarning` |
| v0.13.0 | 旧 API 触发 `FutureWarning` |
| v1.0.0 | 移除旧 API |

### 弃用实现

```python
import warnings
from typing import Type

# 保留实际实现
def _select_interface_impl(system: str = None) -> Type[BaseInterface]:
    # ... 原有 select_interface 逻辑

def select_interface(system: str = None) -> Type[BaseInterface]:
    """已弃用，请使用 NowPlaying 类代替。"""
    warnings.warn(
        "select_interface() is deprecated. Use NowPlaying instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return _select_interface_impl(system)

# NowPlayingInterface 别名弃用
def __getattr__(name: str):
    if name == "NowPlayingInterface":
        warnings.warn(
            "NowPlayingInterface is deprecated. Use NowPlaying instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return select_interface()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
```

## 测试策略

1. **单元测试** — 测试 `NowPlaying` 类的所有属性和方法
2. **集成测试** — 测试各平台后端与 `NowPlaying` 的交互
3. **兼容性测试** — 确保旧 API 仍能正常工作
4. **弃用警告测试** — 确保弃用警告正确触发
5. **回调测试** — 测试同步和异步回调的正确执行

## 文档更新

- 更新 README.md 的 Quick Start 示例
- 更新 Sphinx 文档
- 添加迁移指南（旧 API → 新 API）