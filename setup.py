import ast
import pathlib
import sys
from setuptools import find_packages, setup


def read_version():
    """
    Read the version from `asterios/__version__.py` without import
    module to avoid side effect.
    """
    module_src = (
        pathlib.Path(__file__).parent / "asterios" / "__version__.py"
    ).read_text()
    for statment in ast.parse(module_src).body:
        if isinstance(statment, ast.Assign):
            if statment.targets[0].id == "__version__":
                version = statment.value.s
                break
    else:
        exit(
            "The `__version__` variable is not defined"
            " in the `asterios.__version__` module"
        )

    return version


setup(
    name="asterios",
    version=read_version(),
    description="Asterios escape game server",
    keywords="Asterios escape game server",
    author="vincent.maillol@gmail.com",
    author_email="vincent.maillol@gmail.com",
    url="https://github.com/Maillol/asterios",
    license="GPLv3",
    packages=["asterios"]
    + [
        "asterios.{}".format(subpackage)
        for subpackage in find_packages(where="./asterios")
    ],
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Topic :: Games/Entertainment :: Puzzle Games",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.7",
        "aiohttp-security>=0.2",
        "aiohttp-pedantic>=1.6.1",
        "attrs>=17.4",
        "voluptuous>=0.10",
        "pyyaml>=3.12",
        "basicauth>=0.4",
    ],
)
