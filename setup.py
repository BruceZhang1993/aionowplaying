# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aionowplaying', 'aionowplaying.interface']

package_data = \
{'': ['*']}

install_requires = \
['pydantic']

extras_require = \
{':sys_platform == "darwin"': ['pyobjc-framework-MediaPlayer',
                               'pyobjc-framework-Cocoa'],
 ':sys_platform == "linux"': ['dbus-next'],
 ':sys_platform == "win32"': ['winsdk']}

setup_kwargs = {
    'name': 'aionowplaying',
    'version': '0.10.0',
    'description': 'A cross-platform Now Playing client',
    'long_description': '[![GitHub Workflow Status][ci-shield]][ci-url]\n[![GPL3.0 License][license-shield]][license-url]\n\n# aionowplaying\nA cross-platform Now Playing client\n\n## Usage\n```shell\n# Using pip\npip install aionowplaying\n# Using poetry\npoetry add aionowplaying\n```\n\n## Documentation\n_TODO_\nsee tests for now.\n\n## Development\n```shell\npoetry install\npoetry run pytest -v\n```\n\n## License\nGPL-3.0\n\n<!-- MARKDOWN LINKS & IMAGES -->\n[ci-shield]: https://img.shields.io/github/actions/workflow/status/BruceZhang1993/aionowplaying/ci.yml?style=for-the-badge\n[license-shield]: https://img.shields.io/github/license/BruceZhang1993/aionowplaying.svg?style=for-the-badge\n[ci-url]: https://github.com/BruceZhang1993/aionowplaying/actions/workflows/ci.yml\n[license-url]: https://github.com/BruceZhang1993/aionowplaying/blob/master/LICENSE.txt\n',
    'author': 'Bruce Zhang',
    'author_email': 'zttt183525594@gmail.com',
    'maintainer': 'Bruce Zhang',
    'maintainer_email': 'zttt183525594@gmail.com',
    'url': 'https://github.com/BruceZhang1993/aionowplaying',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<3.12',
}


setup(**setup_kwargs)

