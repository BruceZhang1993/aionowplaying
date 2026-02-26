import os
import sys

project = "aionowplaying"
author = "Bruce Zhang"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

autosummary_generate = True
autodoc_member_order = "bysource"

# Ensure local package is importable when building docs.
sys.path.insert(0, os.path.abspath("../src"))

# Cross-platform optional runtime dependencies that may be absent on RTD.
autodoc_mock_imports = [
    "dbus_fast",
    "dbus_fast.aio",
    "dbus_fast.service",
    "Foundation",
    "AppKit",
    "MediaPlayer",
    "winrt",
    "winrt.system",
    "winrt.windows",
    "winrt.windows.foundation",
    "winrt.windows.media",
    "winrt.windows.media.playback",
    "winrt.windows.storage",
    "winrt.windows.storage.streams",
]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

templates_path = ["_templates"]
html_static_path = ["_static"]
html_theme = "alabaster"
