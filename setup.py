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
    'version': '0.9.4',
    'description': 'A cross-platform Now Playing client',
    'long_description': '',
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

