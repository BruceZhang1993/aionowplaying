# src/aionowplaying — 源码指南

## 结构

```
src/aionowplaying/
├── __init__.py              # 公开 API，__all__ 在此
├── nowplaying.py            # NowPlaying 门面类（推荐入口）
└── interface/
    ├── __init__.py          # select_interface() 工厂 + INTERFACES_BY_SYSTEM 映射
    ├── base.py              # BaseInterface、枚举、Pydantic 模型
    ├── mpris2.py            # Linux — D-Bus MPRIS2
    ├── windows.py           # Windows — SMTC
    └── macos.py             # macOS — MediaPlayer
```

策略模式：`BaseInterface`（抽象）→ 平台实现 → `INTERFACES_BY_SYSTEM` 按 `sys.platform` 选择。

## 关键约定

- 属性访问用 `set_playback_property()` / `get_playback_property()`，别碰 `_properties`
- 能力标志 `CanPlay` / `CanPause` / `CanSeek` 等必须显式 `True`，否则系统不显示控件
- 回调方法（`on_play` 等）必须是 `async`
- 时间值：底层微秒 int，`NowPlaying` 层 `timedelta`
- `select_interface()` 调用方式已废弃，统一使用 `NowPlaying`（`src/aionowplaying/nowplaying.py`）
- 所有时间值为**微秒**（int），`NowPlaying` 对外包装为 `timedelta`

## 平台差异

| 平台 | 坑 |
|------|------|
| Linux | LSP 报 `"s" is not defined` 是 D-Bus 类型签名，忽略 |
| Windows | 回调不在主线程，`_run_task()` 用 `asyncio.run_coroutine_threadsafe` |
| macOS | 部分属性只读；切歌时必须同步更新 position（框架 bug workaround） |

详见 [interface/AGENTS.md](interface/AGENTS.md)。

## 扩展

**加属性**：`base.py` 枚举 → 模型字段 → 各平台 `set_playback_property()` 映射

**加回调**：`BaseInterface.on_xxx()` → 平台 handler 调用 → 加测试

**加平台**：`interface/` 新模块 → 继承 `BaseInterface` → 注册到 `INTERFACES_BY_SYSTEM`
