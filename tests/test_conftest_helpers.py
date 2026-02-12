import types

import conftest


def test_platform_omit_patterns_windows(monkeypatch):
    monkeypatch.setattr(conftest.sys, "platform", "win32")
    assert conftest._platform_omit_patterns() == [
        "*/interface/macos.py",
        "*/interface/mpris2.py",
    ]


def test_platform_omit_patterns_macos(monkeypatch):
    monkeypatch.setattr(conftest.sys, "platform", "darwin")
    assert conftest._platform_omit_patterns() == [
        "*/interface/windows.py",
        "*/interface/mpris2.py",
    ]


def test_platform_omit_patterns_linux(monkeypatch):
    monkeypatch.setattr(conftest.sys, "platform", "linux")
    assert conftest._platform_omit_patterns() == [
        "*/interface/windows.py",
        "*/interface/macos.py",
    ]


class _FakeCov:
    def __init__(self, run_omit=None, report_omit=None, started=False):
        self.config = types.SimpleNamespace(
            run_omit=run_omit,
            report_omit=report_omit,
        )
        self._started = started
        self.options = {}
        self.stopped = False
        self.started = False

    def stop(self):
        self.stopped = True

    def start(self):
        self.started = True

    def set_option(self, key, value):
        self.options[key] = value


def test_apply_omit_no_cov():
    conftest._apply_omit(None, ["*/interface/windows.py"])


def test_apply_omit_merges_and_sets_options_when_not_started():
    cov = _FakeCov(run_omit=["a.py"], report_omit=["b.py"], started=False)
    conftest._apply_omit(cov, ["b.py", "c.py"])
    assert cov.options["run:omit"] == ["a.py", "b.py", "c.py"]
    assert cov.options["report:omit"] == ["b.py", "c.py"]
    assert cov.stopped is False
    assert cov.started is False


def test_apply_omit_restarts_when_started():
    cov = _FakeCov(run_omit=None, report_omit=None, started=True)
    conftest._apply_omit(cov, ["c.py"])
    assert cov.options["run:omit"] == ["c.py"]
    assert cov.options["report:omit"] == ["c.py"]
    assert cov.stopped is True
    assert cov.started is True
