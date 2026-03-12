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
    on_seek=lambda pos: my_player.seek(pos),
    on_stop=lambda: my_player.stop(),
)
```

### 运行时更新 API

**属性赋值方式：**

```python
player.title = "New Song"
player.artist = ["New Artist"]
player.position = timedelta(seconds=60)
player.playing = True
```

**批量更新方式：**

```python
player.update(
    title="New Song",
    artist=["New Artist"],
    album="New Album",
    position=timedelta(seconds=30),
)
```

**播放状态便捷方法：**

```python
player.playing()    # 设置状态为 Playing
player.paused()     # 设置状态为 Paused
player.stopped()    # 设置状态为 Stopped
```

### 时间单位

使用 `datetime.timedelta` 表示时间，内部自动转换为微秒：

```python
player.duration = timedelta(minutes=3, seconds=30)  # 3:30
player.position = timedelta(seconds=45)
```

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

# 保留（不弃用）
BaseInterface      # 高级用户可继承
PlaybackStatus     # 枚举
LoopStatus         # 枚举
PlaybackProperties # Pydantic 模型
```

## 实现细节

### `NowPlaying` 类

```python
class NowPlaying:
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
    ): ...

    # 属性 setter/getter
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
    def duration(self) -> timedelta | None: ...
    @duration.setter
    def duration(self, value: timedelta): ...

    @property
    def position(self) -> timedelta | None: ...
    @position.setter
    def position(self, value: timedelta): ...

    # 批量更新
    def update(self, **kwargs) -> None: ...

    # 播放状态
    def playing(self) -> None: ...
    def paused(self) -> None: ...
    def stopped(self) -> None: ...

    # 生命周期
    async def start(self) -> None: ...
    async def stop(self) -> None: ...
```

### 内部实现

`NowPlaying` 内部持有 `BaseInterface` 实例，代理所有调用：

```python
class NowPlaying:
    def __init__(self, ...):
        self._interface = select_interface()(name)
        self._callbacks = {...}
        self._setup_callbacks()

    def _setup_callbacks(self):
        # 根据注册的回调设置能力
        if self._callbacks.get('on_play'):
            self._interface.set_playback_property(
                PlaybackPropertyName.CanPlay, True
            )
        # ...
```

## 弃用计划

| 版本 | 行为 |
|------|------|
| v0.12.0 | 新 API 发布，旧 API 触发 `DeprecationWarning` |
| v0.13.0 | 旧 API 触发 `FutureWarning` |
| v1.0.0 | 移除旧 API |

### 弃用警告示例

```python
import warnings

def select_interface(system: str = None) -> Type[BaseInterface]:
    warnings.warn(
        "select_interface() is deprecated. Use NowPlaying instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    # ... 现有实现
```

## 测试策略

1. **单元测试** — 测试 `NowPlaying` 类的所有属性和方法
2. **集成测试** — 测试各平台后端与 `NowPlaying` 的交互
3. **兼容性测试** — 确保旧 API 仍能正常工作
4. **弃用警告测试** — 确保弃用警告正确触发

## 文档更新

- 更新 README.md 的 Quick Start 示例
- 更新 Sphinx 文档
- 添加迁移指南（旧 API → 新 API）