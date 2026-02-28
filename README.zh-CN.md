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
import asyncio
import aionowplaying as aionp

backend = aionp.select_interface()("My Player")
backend.set_property(aionp.PropertyName.Identity, "My Player")
backend.set_playback_property(
    aionp.PlaybackPropertyName.PlaybackStatus,
    aionp.PlaybackStatus.Playing,
)
asyncio.run(backend.start())
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
