import sys


def _platform_omit_patterns() -> list[str]:
    if sys.platform.startswith("win"):
        return [
            "*/interface/macos.py",
            "*/interface/mpris2.py",
        ]
    if sys.platform == "darwin":
        return [
            "*/interface/windows.py",
            "*/interface/mpris2.py",
        ]
    return [
        "*/interface/windows.py",
        "*/interface/macos.py",
    ]


def _apply_omit(cov, omit: list[str]) -> None:
    if cov is None:
        return
    run_existing = list(cov.config.run_omit or [])
    report_existing = list(getattr(cov.config, "report_omit", []) or [])
    merged_run = sorted(set(run_existing + omit))
    merged_report = sorted(set(report_existing + omit))
    was_started = bool(getattr(cov, "_started", False))
    if was_started:
        cov.stop()
    cov.set_option("run:omit", merged_run)
    cov.set_option("report:omit", merged_report)
    if was_started:
        cov.start()


def pytest_configure(config):
    cov_plugin = config.pluginmanager.getplugin("_cov")
    if cov_plugin is None:
        return
    cov_controller = getattr(cov_plugin, "cov_controller", None)
    if cov_controller is None:
        return
    omit = _platform_omit_patterns()
    _apply_omit(getattr(cov_controller, "cov", None), omit)
    _apply_omit(getattr(cov_controller, "combining_cov", None), omit)
