"""
This module contains factory that can be create object for the
argument `type` of argparse.ArgumentParser.add_argument()` method.
"""

import abc
from argparse import ArgumentTypeError
from pathlib import Path

from voluptuous import Invalid
import yaml


class ConfigModifierType(metaclass=abc.ABCMeta):
    """
    Factory for creating configuration modifier objects types can be 
    used as `type` argument to the `ArgumentParser.add_argument()` method.
    """

    def __init__(self, config):
        self.config = config

    @abc.abstractmethod
    def __call__(self, value: str):
        """
        This method tries to onvert `value` to a type and store it or
        raise an ArgumentTypeError.
        """

    @abc.abstractmethod
    def modify_config(self):
        """
        Update the `config` using the `value`
        stored with the __call__ mathod.
        """


class ConfigUpdaterType(ConfigModifierType):
    """
    >>> conf = {}
    >>> action = ConfigUpdaterType(
    ...     conf, [(dict, 'a'), (dict, 'b'), (int, 'c')])
    >>> action('3').modify_config()
    >>> conf
    {'a': {'b': {'c': 3}}}

    >>> conf = {}
    >>> action = ConfigUpdaterType(
    ...     conf, [(list, 'a'), (str, None)])
    >>> action('X').modify_config()
    >>> action('Y').modify_config()
    >>> conf
    {'a': ['X', 'Y']}

    >>> conf = {}
    >>> action = ConfigUpdaterType(
    ...     conf, [(list, 'a'), (dict, None), (int, 'b')])
    >>> action('3').modify_config()
    >>> conf
    {'a': [{'b': 3}]}

    >>> action('a')
    Traceback (most recent call last):
    ...
    argparse.ArgumentTypeError: invalid literal for int() with base 10: 'a'

    >>> conf = {}
    >>> action = ConfigUpdaterType(
    ...     conf, [(list, 'a'), (dict, None), ('constB', 'b')])
    >>> action('constB').modify_config()
    >>> conf 
    {'a': [{'b': 'constB'}]}

    >>> action('constC')
    Traceback (most recent call last):
    ...
    argparse.ArgumentTypeError: 'constB' is expected (got 'constC')
    """

    def __init__(self, config, dest):
        super().__init__(config)
        self.dest = dest

    def __call__(self, value):
        """
        Casts `value` to the `expected_type`.
        If the `expected_type` is note a type, it means that a constant
        is expected and the method checks if the `value` is equal to this
        constant.

        Returns a new initialized ConfigUpdater
        """
        expected_type_or_constant = self.dest[-1][0]

        if isinstance(expected_type_or_constant, type):
            try:
                value = expected_type_or_constant(value)
            except Exception as error:
                raise ArgumentTypeError(error)

        elif expected_type_or_constant != value:
            raise ArgumentTypeError('{!r} is expected (got {!r})'.format(
                expected_type_or_constant, value))

        copy = type(self)(self.config, self.dest)
        copy.validated_value = value
        return copy

    def modify_config(self):
        """
        Update the `config` using the `validated_value`.   
        """
        config = self.config
        for next_type, arg in self.dest:
            if isinstance(config, list):
                if next_type is dict:
                    new_config = {}
                    config.append(new_config)
                    config = new_config
                elif next_type is list:
                    raise NotImplementedError('List of list is not supported')
                else:
                    config.append(self.validated_value)

            elif isinstance(config, dict):
                if next_type is dict:
                    new_config = {}
                    config = config.setdefault(arg, new_config)
                elif next_type is list:
                    new_config = []
                    config = config.setdefault(arg, new_config)
                else:
                    config[arg] = self.validated_value


class ConfigInitializerType(ConfigModifierType):
    """
    Base class to initialize configuration from a file.
    """

    def __init__(self, config, config_validator,
                 default_path=None, default_is_required=False):
        """
        config - The configuration.
        config_validator - A voluptuous.Schema object.
        default_path - The path to the default configuration file.
            the `default_path` will be used during the `modify_config`
            call if this `ConfigInitializerType` object has not been 
            called.
        default_is_required - if True, the `default_path` should exist
        """
        if default_is_required and default_path is None:
            raise ValueError('You should provide the `default_path`'
                             ' if default_is_required is True')

        super().__init__(config)
        if default_path is not None:
            default_path = Path(default_path)
        self.default_path_to_config = default_path
        self.config_validator = config_validator
        self.default_is_required = default_is_required
        self.new_validated_config = NotImplemented

    @abc.abstractmethod
    def _load(self, config_file):
        """
        Load the configuration in `config_file` and return it. 
        """

    def _load_and_validate(self, path_to_config):
        """loads and validates a configuration from a file."""
        try:
            with path_to_config.open() as config_file:
                new_config = self._load(config_file)
                return self.config_validator(new_config)
        except (OSError, Invalid) as error:
            raise ArgumentTypeError(str(error))

    def __call__(self, value):
        path_to_config = Path(value)
        self.new_validated_config = self._load_and_validate(path_to_config)
        return self

    def modify_config(self):
        new_validated_config = self.new_validated_config
        if new_validated_config is NotImplemented:

            if self.default_path_to_config is not None:
                if self.default_is_required \
                        and not self.default_path_to_config.exists():
                    raise ArgumentTypeError(str(error))

                if self.default_path_to_config.exists():
                    new_validated_config = self._load_and_validate(
                        self.default_path_to_config)
                else:
                    # If an error is raised here, the Voluptuous Schema
                    # has not been correctly defined.
                    new_validated_config = self.config_validator({})

        self.config.clear()
        self.config.update(new_validated_config)


class YamlConfigInitializerType(ConfigInitializerType):
    """
    ConfigInitializerType for yaml file.
    """

    def _load(self, config_file):
        return yaml.load(config_file.read())
