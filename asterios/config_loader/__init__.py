"""
This package provides classes to generate a command line arguments parser
from voluptuous schema.

The command line arguments parser provides parameters to:
    - Load a configuration from a file
    - Update loaded configuration from command line arguments
    - Print help about configuration parameters
"""

from voluptuous import (Invalid,
                        Optional as _Optional,
                        Required as _Required,
                        Schema)

from .argument_parser import ArgumentParserBuilder


class Optional(_Optional):  # pylint: disable=too-few-public-methods
    """
    This class is like `voluptuous.Optional` class except that
    accept help parameter using by `ArgumentParser`.
    """

    def __init__(self, *args, **kwargs):
        self.help = kwargs.pop('help', '')
        super().__init__(*args, **kwargs)


class Required(_Required):  # pylint: disable=too-few-public-methods
    """
    This class is like `voluptuous.Required` class except that
    accept help parameter using by `ArgumentParser`.
    """

    def __init__(self, *args, **kwargs):
        self.help = kwargs.pop('help', '')
        super().__init__(*args, **kwargs)


__all__ = ['ArgumentParser', 'Invalid', 'Optional', 'Required', 'Schema']
