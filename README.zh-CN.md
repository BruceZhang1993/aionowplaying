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

一个支持 Linux（MPRIS2）、macOS、Windows 的跨平台 Now Playing 客户端库。

## 功能特性

- 统一的 Python 接口，便于在不同系统上集成 Now Playing 功能。
- 运行时自动选择平台后端实现。
- 基于 Pydantic 的类型化播放属性模型。
- 简化的 Fluent API，支持 `timedelta` 时间类型。

## 安装

```shell
pip install aionowplaying
```

如果你使用 `uv`：

```shell
uv add aionowplaying
```

## 快速开始

```python
import asyncio
from datetime import timedelta
from aionowplaying import NowPlaying

# 创建播放器并设置元数据和回调
player = NowPlaying(
    "My Player",
    metadata={
        "title": "歌曲名称",
        "artist": ["艺术家"],
        "album": "专辑",
        "duration": timedelta(minutes=3, seconds=30),
    },
    on_play=lambda: my_player.play(),
    on_pause=lambda: my_player.pause(),
    on_next=lambda: my_player.next(),
)

# 播放过程中更新元数据
player.title = "新歌曲"
player.position = timedelta(seconds=60)
player.set_playing()

# 启动后端
asyncio.run(player.start())
```

### 高级用法

如需更精细的控制，可以继承 `BaseInterface`：

```python
from aionowplaying import BaseInterface

class MyPlayer(BaseInterface):
    async def on_play(self):
        # 自定义实现
        pass

    async def on_pause(self):
        # 自定义实现
        pass
```

## BaseInterface 平台实现情况

下表说明 `BaseInterface` 每个方法在各平台后端中的实现覆盖情况。这里关注的是“是否有原生后端映射”，而不只是“Python 里能否覆写”。

- `🟢 原生实现`：平台后端直接实现或会从系统回调触发。
- `🟡 部分实现`：可用，但存在限制，或语义与基类约定不完全一致。
- `⚪ 仅缓存`：只保存在本地状态中，不会映射到系统原生 API。
- `🔴 未实现`：没有平台特定实现。基类默认空实现统一视为未实现。

当应用提供 tracklist 回调时，Linux MPRIS2 后端会暴露 TrackList 属性、方法和信号。

### 构造与生命周期

| 方法 | Linux (MPRIS2) | macOS | Windows |
| --- | --- | --- | --- |
| `__init__` | 🟢 原生实现<br>D-Bus 初始化 | 🟢 原生实现<br>媒体中心初始化 | 🟢 原生实现<br>SMTC 初始化 |
| `start` | 🟢 原生实现<br>D-Bus 连接与导出 | 🟢 原生实现<br>空操作 | 🟢 原生实现<br>空操作 |
| `stop` | 🟢 原生实现<br>D-Bus 断开 | 🔴 未实现 | 🟡 部分实现<br>仅本地标志 |

### 应用级回调

| 方法 | Linux (MPRIS2) | macOS | Windows |
| --- | --- | --- | --- |
| `on_fullscreen` | 🟢 原生实现<br>`Fullscreen` setter | 🔴 未实现 | 🔴 未实现 |
| `on_raise` | 🟢 原生实现<br>`Raise` 命令 | 🔴 未实现 | 🔴 未实现 |
| `on_quit` | 🟢 原生实现<br>`Quit` 命令 | 🔴 未实现 | 🔴 未实现 |

### 播放控制回调

| 方法 | Linux (MPRIS2) | macOS | Windows |
| --- | --- | --- | --- |
| `on_loop_status` | 🟢 原生实现<br>`LoopStatus` setter | 🟢 原生实现<br>重复模式命令 | 🟢 原生实现<br>重复模式请求 |
| `on_rate` | 🟢 原生实现<br>`Rate` setter | 🟢 原生实现<br>倍速命令 | 🟢 原生实现<br>倍速请求 |
| `on_shuffle` | 🟢 原生实现<br>`Shuffle` setter | 🟢 原生实现<br>随机播放命令 | 🟢 原生实现<br>随机播放请求 |
| `on_volume` | 🟢 原生实现<br>`Volume` setter | 🔴 未实现 | 🟡 部分实现<br>只读音量状态 |
| `on_next` | 🟢 原生实现<br>`Next` 命令 | 🟢 原生实现<br>下一曲命令 | 🟢 原生实现<br>Next 按钮 |
| `on_previous` | 🟢 原生实现<br>`Previous` 命令 | 🟢 原生实现<br>上一曲命令 | 🟢 原生实现<br>Previous 按钮 |
| `on_pause` | 🟢 原生实现<br>`Pause` 命令 | 🟢 原生实现<br>暂停命令 | 🟢 原生实现<br>Pause 按钮 |
| `on_play_pause` | 🟢 原生实现<br>`PlayPause` 命令 | 🟢 原生实现<br>切换命令 | 🔴 未实现 |
| `on_play` | 🟢 原生实现<br>`Play` 命令 | 🟢 原生实现<br>播放命令 | 🟢 原生实现<br>Play 按钮 |
| `on_stop` | 🟢 原生实现<br>`Stop` 命令 | 🟡 部分实现<br>依赖框架支持 | 🟢 原生实现<br>Stop 按钮 |

### 位置与 URI 回调

| 方法 | Linux (MPRIS2) | macOS | Windows |
| --- | --- | --- | --- |
| `on_seek` | 🟢 原生实现<br>offset seek | 🟡 部分实现<br>绝对位置 | 🟡 部分实现<br>绝对位置 |
| `on_open_uri` | 🟢 原生实现<br>`OpenUri` 命令 | 🔴 未实现 | 🔴 未实现 |
| `on_set_position` | 🟢 原生实现<br>`SetPosition` 命令 | 🟢 原生实现<br>位置命令 | 🟢 原生实现<br>位置请求 |
| `seeked` | 🟢 原生实现<br>`Seeked` 信号 | 🔴 未实现 | 🔴 未实现 |

### 属性接口

| 方法 | Linux (MPRIS2) | macOS | Windows |
| --- | --- | --- | --- |
| `set_property` | 🟢 原生实现<br>player 属性 | ⚪ 仅缓存<br>无 player 级 API | ⚪ 仅缓存<br>无 player 级 API |
| `set_playback_property` | 🟢 原生实现<br>playback 属性 | 🟡 部分实现<br>部分字段不支持 | 🟡 部分实现<br>部分字段仅本地 |
| `set_tracklist_property` | 🟢 原生实现<br>TrackList 属性<br>含 D-Bus 更新通知 | ⚪ 仅缓存 | ⚪ 仅缓存 |
| `get_property` | 🟢 原生实现<br>player 属性 | ⚪ 仅缓存<br>缓存值 | ⚪ 仅缓存<br>缓存值 |
| `get_playback_property` | 🟢 原生实现<br>playback 属性 | 🟡 部分实现<br>`Position`/`Rate` 原生，其余缓存 | ⚪ 仅缓存<br>缓存值 |
| `get_tracklist_property` | 🟢 原生实现<br>TrackList 属性 | ⚪ 仅缓存<br>缓存值 | ⚪ 仅缓存<br>缓存值 |

## 文档

- 接口/API 文档：https://aionowplaying.readthedocs.io/en/latest/
- API 参考页：https://aionowplaying.readthedocs.io/en/latest/api.html

本地构建文档：

```shell
sphinx-build -b html docs docs/_build/html
```

## 开发

安装开发依赖并运行测试：

```shell
uv sync --dev
uv run pytest -v
```

## 许可证

本项目采用 GPL-3.0-only 许可证，详见 [LICENSE.txt](LICENSE.txt)。

## 贡献

欢迎贡献代码！请遵循以下指南。

### 报告问题

如果你发现了 bug 或有新功能建议：

1. 先搜索现有 issues 避免重复
2. 使用合适的 issue 模板：
   - **Bug 报告**：用于报告 bug 和错误
   - **功能请求**：用于建议新功能
   - **问题/其他**：用于其他咨询
3. 尽可能提供详细信息：
   - Bug：请提供复现步骤、预期与实际行为、环境信息
   - 功能：请说明用例和价值

### 提交 Pull Request

1. Fork 仓库并从 `main` 创建功能分支
2. 本地运行测试：`uv run pytest -v`
3. 确保代码符合项目规范
4. 提交信息清晰明了
5. 推送代码并创建 PR
6. 填写 PR 模板，提供所有相关信息

### 开发环境设置

```shell
# 克隆你的 fork
git clone https://github.com/YOUR_USERNAME/aionowplaying.git
cd aionowplaying

# 安装依赖
uv sync --dev

# 运行测试
uv run pytest -v

# 运行代码检查（如果可用）
uv run ruff check .
```
