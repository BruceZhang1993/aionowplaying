# aionowplaying

[English](README.md) | [中文](README.zh-CN.md)

[![CI](https://github.com/BruceZhang1993/aionowplaying/actions/workflows/ci.yml/badge.svg)](https://github.com/BruceZhang1993/aionowplaying/actions/workflows/ci.yml)
[![codecov](https://codecov.io/github/BruceZhang1993/aionowplaying/graph/badge.svg?token=RQ93AOUTDC)](https://codecov.io/github/BruceZhang1993/aionowplaying)
[![PyPI version](https://img.shields.io/pypi/v/aionowplaying.svg)](https://pypi.org/project/aionowplaying/)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE.txt)

A cross-platform Now Playing client for Linux (MPRIS2), macOS, and Windows.

## Features

- Unified Python interface for Now Playing integration across platforms.
- Platform-specific backends selected automatically at runtime.
- Typed playback/property models powered by Pydantic.

## Installation

```shell
pip install aionowplaying
```

If you use `uv`:

```shell
uv add aionowplaying
```

## Quick Start

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

## Documentation

- Interface/API documentation: https://aionowplaying.readthedocs.io/en/latest/
- API reference page: https://aionowplaying.readthedocs.io/en/latest/api.html

Build docs locally:

```shell
sphinx-build -b html docs docs/_build/html
```

## Development

Install dependencies and run tests:

```shell
uv sync --dev
uv run pytest -v
```

## License

This project is licensed under GPL-3.0-only. See [LICENSE.txt](LICENSE.txt).

## Contributing

Contributions are welcome! Please follow the guidelines below.

### Reporting Issues

If you find a bug or have a feature request:

1. Search existing issues to avoid duplicates
2. Use the appropriate issue template:
   - **Bug Report**: For reporting bugs and errors
   - **Feature Request**: For suggesting new features
   - **Question/Other**: For other inquiries
3. Provide as much detail as possible:
   - For bugs: steps to reproduce, expected vs actual behavior, environment details
   - For features: use case and why it would be helpful

### Pull Requests

1. Fork the repository and create a feature branch from `main`
2. Run tests locally: `uv run pytest -v`
3. Ensure code follows project conventions
4. Write clear commit messages
5. Push your changes and create a pull request
6. Fill out the PR template with all relevant details

### Development Setup

```shell
# Clone your fork
git clone https://github.com/YOUR_USERNAME/aionowplaying.git
cd aionowplaying

# Install dependencies
uv sync --dev

# Run tests
uv run pytest -v

# Run linting (if available)
uv run ruff check .
```
