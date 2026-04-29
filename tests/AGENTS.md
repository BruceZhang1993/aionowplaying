# tests — 测试指南

## 运行

```bash
uv run pytest -v                                    # 全部
uv run pytest -v tests/test_base_interface.py       # 单文件
uv run pytest -v --cov --cov-branch                 # 带覆盖率
dbus-launch --exit-with-session uv run pytest -v    # Linux container without desktop
```

`pytest.ini` 设 `asyncio_mode = auto`，但现有测试显式标了 `@pytest.mark.asyncio`。

## 文件清单

| 文件 | 范围 | 备注 |
|------|------|------|
| `test_base_interface.py` | 跨平台基础逻辑 | |
| `test_interface_select.py` | 工厂选择 | |
| `test_nowplaying.py` | NowPlaying 门面 | 最大，700+ 行 |
| `test_mpris2_interface.py` | Linux MPRIS2 | `pytestmark` 自动 skip 其他平台 |
| `test_windows_interface.py` | Windows SMTC | 同上 |
| `test_macos_interface.py` | macOS MediaPlayer | 同上 |
| `test_coverage_additions.py` | 边界 case | |

## 覆盖率

`conftest.py` 按当前平台自动 omit 其他平台模块的覆盖率，无需手动配置。

## CI

矩阵：Ubuntu / Windows / macOS × Python 3.10–3.14。macOS 测试退出码 137 允许通过。

Release：git tag 必须与 `pyproject.toml` 中 `version` 完全一致（如 `v0.11.3`）。
