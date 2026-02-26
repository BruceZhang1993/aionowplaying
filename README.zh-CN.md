# aionowplaying

[English](README.md) | [中文](README.zh-CN.md)

[![CI](https://github.com/BruceZhang1993/aionowplaying/actions/workflows/ci.yml/badge.svg)](https://github.com/BruceZhang1993/aionowplaying/actions/workflows/ci.yml)
[![codecov](https://codecov.io/github/BruceZhang1993/aionowplaying/graph/badge.svg?token=RQ93AOUTDC)](https://codecov.io/github/BruceZhang1993/aionowplaying)
[![PyPI version](https://img.shields.io/pypi/v/aionowplaying.svg)](https://pypi.org/project/aionowplaying/)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE.txt)

一个支持 Linux（MPRIS2）、macOS、Windows 的跨平台 Now Playing 客户端库。

## 功能特性

- 统一的 Python 接口，便于在不同系统上集成 Now Playing 功能。
- 运行时自动选择平台后端实现。
- 基于 Pydantic 的类型化播放属性模型。

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
import aionowplaying as aionp

backend = aionp.NowPlayingInterface("My Player")
backend.set_property(aionp.PropertyName.Identity, "My Player")
backend.set_playback_property(
    aionp.PlaybackPropertyName.PlaybackStatus,
    aionp.PlaybackStatus.Playing,
)
```

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
