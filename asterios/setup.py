from setuptools import setup

setup(
    name='asterios',
    version='1.0a1',
    description='Escape game server',
    keywords='escape game server',
    author='Vincent Maillol',
    author_email='vincent.maillol@gmail.com',
    url='https://github.com/maillol/asterios',
    license='GPLv3',
    packages=['asterios'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
    ],
    python_requires='>=3.5',
    install_requires=['aiohttp>=2.3',
                      'attrs>=17.4',
                      'voluptuous>=0.10.5']
)
