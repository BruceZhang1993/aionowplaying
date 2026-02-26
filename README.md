# aionowplaying
A cross-platform Now Playing client

## Status

[![codecov](https://codecov.io/github/BruceZhang1993/aionowplaying/graph/badge.svg?token=RQ93AOUTDC)](https://codecov.io/github/BruceZhang1993/aionowplaying)

## Usage
```shell
# Using pip
pip install aionowplaying
# Using poetry
poetry add aionowplaying
```

## Documentation
API docs are published on Read the Docs:
https://aionowplaying.readthedocs.io/

Build locally:
```shell
sphinx-build -b html docs docs/_build/html
```

## Development
```shell
poetry install
poetry run pytest -v
```

## License
[![GPL3.0 License][license-shield]][license-url]

<!-- MARKDOWN LINKS & IMAGES -->
[ci-shield]: https://img.shields.io/github/actions/workflow/status/BruceZhang1993/aionowplaying/ci.yml?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/BruceZhang1993/aionowplaying.svg?style=for-the-badge
[ci-url]: https://github.com/BruceZhang1993/aionowplaying/actions/workflows/ci.yml
[license-url]: https://github.com/BruceZhang1993/aionowplaying/blob/master/LICENSE.txt
