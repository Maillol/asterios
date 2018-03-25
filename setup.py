from setuptools import setup

setup(
    name='asterios',
    version='0.0.1',
    description='Asterios escape game server',
    keywords='Asterios escape game server',
    author='vincent.maillol@gmail.com',
    author_email='vincent.maillol@gmail.com',
    url='https://github.com/Maillol/asterios',
    license='GPLv3',
    packages=['asterios'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Games/Entertainment :: Puzzle Games',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
    ],
    python_requires='>=3.5',
    install_requires=[
        'aiohttp>=3.0',
        'attrs>=17.4',
        'voluptuous>=0.10',
        'pyyaml>=3.12'
    ]
)
