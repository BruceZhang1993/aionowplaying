# OpenUri And URI Activation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 macOS 和 Windows 补齐本地 `OpenUri` 能力，并新增宿主 URI 激活示例文档与 README/Sphinx 引用入口。

**Architecture:** 代码实现分为两部分：一是平台接口层在 macOS 和 Windows 上实现“当前进程主动打开 URI”；二是文档层新增宿主接入示例页面，说明协议注册与 URI 激活为何不能由库单独完成。文档入口统一从 `README.md`、`README.zh-CN.md` 与 Sphinx 目录树暴露。

**Tech Stack:** Python, PyObjC AppKit/Foundation, Windows URI launch APIs, pytest, Sphinx, Markdown, reStructuredText

---

## File Structure

- Modify: `src/aionowplaying/interface/macos.py`
  用 `NSWorkspace` 实现 macOS 平台的本地 URI 打开能力。
- Modify: `src/aionowplaying/interface/windows.py`
  实现 Windows 平台的本地 URI 打开能力，优先走官方 URI 启动 API，必要时保留桌面兼容路径。
- Create: `tests/test_open_uri_helpers.py`
  放置跨平台、可 mock 的 `OpenUri` 行为测试，避免依赖真实桌面环境。
- Modify: `README.md`
  新增 OpenUri 限制说明和示例文档入口。
- Modify: `README.zh-CN.md`
  新增中文版本的 OpenUri 限制说明和示例文档入口。
- Modify: `docs/index.rst`
  把新示例页面挂入 Sphinx 目录树。
- Modify: `docs/quickstart.rst`
  增加到平台 URI 激活说明页的导航。
- Create: `docs/platform-uri-activation.rst`
  作为平台 URI 接入总览页，说明库职责与宿主职责边界。
- Create: `docs/platform-uri-activation-macos.rst`
  macOS 宿主接入示例页面。
- Create: `docs/platform-uri-activation-windows.rst`
  Windows 宿主接入示例页面。

### Task 1: Add Testable OpenUri Behavior For macOS

**Files:**
- Modify: `src/aionowplaying/interface/macos.py`
- Test: `tests/test_open_uri_helpers.py`

- [ ] **Step 1: Write the failing test**

```python
import pytest

from aionowplaying.interface.macos import MacOSInterface


class _FakeWorkspace:
    def __init__(self):
        self.opened = []

    def openURL_(self, url):
        self.opened.append(url)
        return True


@pytest.mark.asyncio
async def test_macos_on_open_uri_uses_workspace(monkeypatch):
    opened = {"url": None}

    class _FakeNSURL:
        @staticmethod
        def URLWithString_(value):
            opened["url"] = value
            return f"NSURL({value})"

    workspace = _FakeWorkspace()
    monkeypatch.setattr("aionowplaying.interface.macos.NSURL", _FakeNSURL)
    monkeypatch.setattr(
        "aionowplaying.interface.macos.NSWorkspace",
        type("NSWorkspace", (), {"sharedWorkspace": staticmethod(lambda: workspace)}),
    )

    it = MacOSInterface("test")
    await it.on_open_uri("https://example.com/song.mp3")

    assert opened["url"] == "https://example.com/song.mp3"
    assert workspace.opened == ["NSURL(https://example.com/song.mp3)"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_open_uri_helpers.py::test_macos_on_open_uri_uses_workspace -v`
Expected: FAIL with `AttributeError` or equivalent because `MacOSInterface` does not implement `on_open_uri`.

- [ ] **Step 3: Write minimal implementation**

```python
from AppKit import NSImage, NSWorkspace


class MacOSInterface(BaseInterface):
    ...

    async def on_open_uri(self, uri: str):
        url = NSURL.URLWithString_(uri)
        if url is None:
            raise ValueError(f"Invalid URI: {uri}")

        workspace = NSWorkspace.sharedWorkspace()
        if not workspace.openURL_(url):
            raise RuntimeError(f"Failed to open URI: {uri}")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_open_uri_helpers.py::test_macos_on_open_uri_uses_workspace -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_open_uri_helpers.py src/aionowplaying/interface/macos.py
git commit -m "feat: 增加 macos openuri 实现" --author="Codex (gpt-5) <noreply@email.openai.com>"
```

### Task 2: Add Testable OpenUri Behavior For Windows

**Files:**
- Modify: `src/aionowplaying/interface/windows.py`
- Test: `tests/test_open_uri_helpers.py`

- [ ] **Step 1: Write the failing test**

```python
import pytest

from aionowplaying.interface.windows import WindowsInterface


@pytest.mark.asyncio
async def test_windows_on_open_uri_calls_opener(monkeypatch):
    called = {"uri": None}

    def fake_open_uri(uri):
        called["uri"] = uri

    monkeypatch.setattr(
        "aionowplaying.interface.windows._open_uri_with_system",
        fake_open_uri,
    )

    it = WindowsInterface("test")
    await it.on_open_uri("https://example.com/song.mp3")

    assert called["uri"] == "https://example.com/song.mp3"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_open_uri_helpers.py::test_windows_on_open_uri_calls_opener -v`
Expected: FAIL because `_open_uri_with_system` or `on_open_uri` does not exist yet.

- [ ] **Step 3: Write minimal implementation**

```python
def _open_uri_with_system(uri: str):
    import webbrowser

    if not webbrowser.open(uri):
        raise RuntimeError(f"Failed to open URI: {uri}")


class WindowsInterface(BaseInterface):
    ...

    async def on_open_uri(self, uri: str):
        _open_uri_with_system(uri)
```

说明：

- 第一版实现优先保证行为可测试和可落地。
- 如果执行阶段确认 `winrt` 的 `Launcher.LaunchUriAsync` 更适合且项目运行环境稳定，可在实现阶段把 helper 改成官方 API，并保留测试边界不变。

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_open_uri_helpers.py::test_windows_on_open_uri_calls_opener -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_open_uri_helpers.py src/aionowplaying/interface/windows.py
git commit -m "feat: 增加 windows openuri 实现" --author="Codex (gpt-5) <noreply@email.openai.com>"
```

### Task 3: Add Error-Handling And Basic Validation Tests

**Files:**
- Modify: `src/aionowplaying/interface/macos.py`
- Modify: `src/aionowplaying/interface/windows.py`
- Test: `tests/test_open_uri_helpers.py`

- [ ] **Step 1: Write the failing tests**

```python
import pytest

from aionowplaying.interface.macos import MacOSInterface
from aionowplaying.interface.windows import _open_uri_with_system


@pytest.mark.asyncio
async def test_macos_on_open_uri_rejects_invalid_url(monkeypatch):
    class _FakeNSURL:
        @staticmethod
        def URLWithString_(_value):
            return None

    monkeypatch.setattr("aionowplaying.interface.macos.NSURL", _FakeNSURL)
    it = MacOSInterface("test")

    with pytest.raises(ValueError, match="Invalid URI"):
        await it.on_open_uri("not a uri")


def test_windows_open_uri_raises_when_system_opener_fails(monkeypatch):
    monkeypatch.setattr("webbrowser.open", lambda _uri: False)

    with pytest.raises(RuntimeError, match="Failed to open URI"):
        _open_uri_with_system("https://example.com")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_open_uri_helpers.py -v`
Expected: FAIL because invalid URI and failure-path handling are not complete yet.

- [ ] **Step 3: Write minimal implementation**

```python
async def on_open_uri(self, uri: str):
    if not uri:
        raise ValueError("Invalid URI: empty string")
    ...


def _open_uri_with_system(uri: str):
    if not uri:
        raise ValueError("Invalid URI: empty string")
    import webbrowser
    if not webbrowser.open(uri):
        raise RuntimeError(f"Failed to open URI: {uri}")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_open_uri_helpers.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_open_uri_helpers.py src/aionowplaying/interface/macos.py src/aionowplaying/interface/windows.py
git commit -m "test: 补充 openuri 错误处理覆盖" --author="Codex (gpt-5) <noreply@email.openai.com>"
```

### Task 4: Add Sphinx Overview Page For URI Activation

**Files:**
- Create: `docs/platform-uri-activation.rst`
- Modify: `docs/index.rst`
- Modify: `docs/quickstart.rst`

- [ ] **Step 1: Write the failing doc references**

在 `docs/index.rst` 的 `toctree` 中预先加入：

```rst
   platform-uri-activation
```

并在 `docs/quickstart.rst` 追加：

```rst
URI Activation
--------------

For macOS and Windows host integration examples, see :doc:`platform-uri-activation`.
```

Expected: 文档构建失败，因为 `platform-uri-activation.rst` 尚不存在。

- [ ] **Step 2: Run docs build to verify it fails**

Run: `sphinx-build -b html docs docs/_build/html`
Expected: FAIL with missing document `platform-uri-activation`.

- [ ] **Step 3: Write minimal implementation**

创建 `docs/platform-uri-activation.rst`：

```rst
URI Activation And Host Integration
===================================

``aionowplaying`` can expose a cross-platform ``on_open_uri`` abstraction, but host
URI activation is still the responsibility of the host application.

This page explains the boundary:

- Opening a URI from within the current process
- Receiving a URI from the operating system via a registered scheme

Platform-specific examples:

- :doc:`platform-uri-activation-macos`
- :doc:`platform-uri-activation-windows`
```

- [ ] **Step 4: Run docs build to verify it passes**

Run: `sphinx-build -b html docs docs/_build/html`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add docs/index.rst docs/quickstart.rst docs/platform-uri-activation.rst
git commit -m "docs: 增加 uri 激活总览页" --author="Codex (gpt-5) <noreply@email.openai.com>"
```

### Task 5: Add macOS Host Integration Example Page

**Files:**
- Create: `docs/platform-uri-activation-macos.rst`
- Modify: `docs/platform-uri-activation.rst`

- [ ] **Step 1: Write the failing doc reference**

在 `docs/platform-uri-activation.rst` 中加入：

```rst
- :doc:`platform-uri-activation-macos`
```

Expected: 构建失败，因为目标页面不存在。

- [ ] **Step 2: Run docs build to verify it fails**

Run: `sphinx-build -b html docs docs/_build/html`
Expected: FAIL with missing document `platform-uri-activation-macos`.

- [ ] **Step 3: Write minimal implementation**

创建 `docs/platform-uri-activation-macos.rst`：

```rst
macOS Host Integration Example
==============================

Why the library alone is not enough
-----------------------------------

``MPNowPlayingInfoCenter`` and ``MPRemoteCommandCenter`` do not register URL schemes
or receive app activation payloads. The host app must do that.

What the host app needs to do
-----------------------------

1. Register a custom URL scheme in ``Info.plist`` via ``CFBundleURLTypes``.
2. Receive the incoming URL in the AppKit lifecycle.
3. Parse the URL and hand the target URI back to the playback layer.

Example
-------

.. code-block:: python

    from Foundation import NSURL

    def handle_incoming_url(raw_url: str, player):
        url = NSURL.URLWithString_(raw_url)
        if url is None:
            raise ValueError(f"Invalid URL: {raw_url}")

        # Replace this parser with your host application's own scheme contract.
        target = raw_url
        return player.load_from_uri(target)
```

- [ ] **Step 4: Run docs build to verify it passes**

Run: `sphinx-build -b html docs docs/_build/html`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add docs/platform-uri-activation.rst docs/platform-uri-activation-macos.rst
git commit -m "docs: 增加 macos uri 激活示例" --author="Codex (gpt-5) <noreply@email.openai.com>"
```

### Task 6: Add Windows Host Integration Example Page

**Files:**
- Create: `docs/platform-uri-activation-windows.rst`
- Modify: `docs/platform-uri-activation.rst`

- [ ] **Step 1: Write the failing doc reference**

在 `docs/platform-uri-activation.rst` 中加入：

```rst
- :doc:`platform-uri-activation-windows`
```

Expected: 构建失败，因为目标页面不存在。

- [ ] **Step 2: Run docs build to verify it fails**

Run: `sphinx-build -b html docs docs/_build/html`
Expected: FAIL with missing document `platform-uri-activation-windows`.

- [ ] **Step 3: Write minimal implementation**

创建 `docs/platform-uri-activation-windows.rst`：

```rst
Windows Host Integration Example
================================

Why the library alone is not enough
-----------------------------------

``SystemMediaTransportControls`` does not register URI schemes or deliver URI
activation events. The host application must own that part.

What the host app needs to do
-----------------------------

1. Register a custom protocol handler.
2. Read the activation URI from the host's activation payload or command-line arguments.
3. Parse the URI and hand the target back to the playback layer.

Example
-------

.. code-block:: python

    import sys

    def handle_protocol_launch(player):
        if len(sys.argv) < 2:
            return None

        raw_url = sys.argv[1]
        target = raw_url
        return player.load_from_uri(target)
```

- [ ] **Step 4: Run docs build to verify it passes**

Run: `sphinx-build -b html docs docs/_build/html`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add docs/platform-uri-activation.rst docs/platform-uri-activation-windows.rst
git commit -m "docs: 增加 windows uri 激活示例" --author="Codex (gpt-5) <noreply@email.openai.com>"
```

### Task 7: Add README Entry Points For The New Docs

**Files:**
- Modify: `README.md`
- Modify: `README.zh-CN.md`

- [ ] **Step 1: Write the failing content expectation**

在两个 README 中都新增一个独立小节，要求至少包含以下要点：

- `on_open_uri` 在 Linux/macOS/Windows 上的能力差异
- macOS / Windows 上“本地打开 URI”和“宿主接收 URI 激活”的区别
- 指向新的文档页面链接

Expected: 当前 README 不满足这些内容要求。

- [ ] **Step 2: Verify current README is missing the content**

Run: `rg -n "URI activation|宿主|on_open_uri|platform-uri-activation" README.md README.zh-CN.md`
Expected: README 中没有指向新文档的入口。

- [ ] **Step 3: Write minimal implementation**

在 `README.md` 中增加类似内容：

```md
## URI Activation

`on_open_uri` is natively exposed through MPRIS on Linux. On macOS and Windows,
the library can open a URI from the current process, but registering a custom
scheme and receiving activation payloads must be implemented by the host app.

See:

- `docs/platform-uri-activation.rst`
- `docs/platform-uri-activation-macos.rst`
- `docs/platform-uri-activation-windows.rst`
```

在 `README.zh-CN.md` 中增加对应中文说明：

```md
## URI 激活

Linux 上的 `on_open_uri` 由 MPRIS 原生暴露。macOS 和 Windows 上，库可以提供
“当前进程主动打开 URI”的能力，但“注册协议并接收系统激活参数”仍需由宿主应用完成。

参见：

- `docs/platform-uri-activation.rst`
- `docs/platform-uri-activation-macos.rst`
- `docs/platform-uri-activation-windows.rst`
```

- [ ] **Step 4: Verify the new content is present**

Run: `rg -n "URI Activation|URI 激活|platform-uri-activation" README.md README.zh-CN.md`
Expected: PASS with new headings and links.

- [ ] **Step 5: Commit**

```bash
git add README.md README.zh-CN.md
git commit -m "docs: 增加 openuri 与 uri 激活说明" --author="Codex (gpt-5) <noreply@email.openai.com>"
```

### Task 8: Run Final Verification Across Tests And Docs

**Files:**
- Test: `tests/test_open_uri_helpers.py`
- Test: `docs/platform-uri-activation.rst`
- Test: `docs/platform-uri-activation-macos.rst`
- Test: `docs/platform-uri-activation-windows.rst`
- Test: `README.md`
- Test: `README.zh-CN.md`

- [ ] **Step 1: Run the targeted Python tests**

Run: `uv run pytest tests/test_open_uri_helpers.py -v`
Expected: PASS

- [ ] **Step 2: Run the existing interface tests that could regress**

Run: `uv run pytest tests/test_macos_interface.py tests/test_windows_interface.py -v`
Expected: PASS on supported platforms or SKIPPED where the platform is unavailable.

- [ ] **Step 3: Build the docs**

Run: `sphinx-build -b html docs docs/_build/html`
Expected: PASS

- [ ] **Step 4: Verify README and docs entry points**

Run: `rg -n "platform-uri-activation" README.md README.zh-CN.md docs/index.rst docs/quickstart.rst`
Expected: PASS with all expected references present.

- [ ] **Step 5: Commit**

```bash
git add src/aionowplaying/interface/macos.py src/aionowplaying/interface/windows.py tests/test_open_uri_helpers.py README.md README.zh-CN.md docs/index.rst docs/quickstart.rst docs/platform-uri-activation.rst docs/platform-uri-activation-macos.rst docs/platform-uri-activation-windows.rst
git commit -m "feat: 完善 openuri 与宿主 uri 激活文档" --author="Codex (gpt-5) <noreply@email.openai.com>"
```
