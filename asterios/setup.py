from setuptools import setup

import os
import sys
sys.path.insert(0, os.path.join(os.path.curdir, 'asterios'))

from __version__ import __version__


if 'a' in __version__:
    development_status = 'Development Status :: 3 - Alpha'
elif 'b' in __version__:
    development_status = 'Development Status :: 4 - Beta'
else:
    development_status = 'Development Status :: 5 - Production/Stable'


setup(
    name='asterios',
    version=__version__,
    description='Escape game server',
    keywords='escape game server',
    author='Vincent Maillol',
    author_email='vincent.maillol@gmail.com',
    url='https://github.com/maillol/asterios',
    license='GPLv3',
    packages=['asterios'],
    classifiers=[
        development_status,
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
    ],
    python_requires='>=3.5',
    install_requires=['aiohttp>=2.3',
                      'attrs>=17.4',
                      'voluptuous>=0.10.5']
)
