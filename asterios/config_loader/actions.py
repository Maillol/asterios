from pathlib import Path

from voluptuous import Invalid
import yaml


class Action:

    class Invalid(Exception):
        """
        Raised when the parameter doesn't have the expected type.
        """

    def __init__(self, config):
        self.config = config


class UpdateAction(Action):
    """
    >>> conf = {}
    >>> action = UpdateAction(
    ...     conf, [(dict, 'a'), (dict, 'b'), (int, 'c')])
    >>> action('3')
    >>> conf == {'a': {'b': {'c': 3}}}
    True

    >>> conf = {}
    >>> action = UpdateAction(
    ...     conf, [(list, 'a'), (dict, None), (int, 'b')])
    >>> action('3')
    >>> conf == {'a': [{'b': 3}]}
    True

    >>> action('a')
    Traceback (most recent call last):
    ...
    asterios.config_loader.actions.Action.Invalid: invalid literal for int() with base 10: 'a'
    """

    def __init__(self, config, dest):
        super().__init__(config)
        self.dest = dest

    def __call__(self, value):
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
                    try:
                        value = next_type(value)
                    except Exception as error:
                        raise self.Invalid(error)
                    config.append(value)

            elif isinstance(config, dict):
                if next_type is dict:
                    new_config = {}
                    config = config.setdefault(arg, new_config)
                elif next_type is list:
                    new_config = []
                    config = config.setdefault(arg, new_config)
                else:
                    try:
                        value = next_type(value)
                    except Exception as error:
                        raise self.Invalid(error)

                    config[arg] = value


class InitFromYamlAction(Action):

    def __init__(self, config, config_validator, default_path):
        super().__init__(config)
        if default_path is not None:
            default_path = Path(default_path)

        self.default_path_to_config = default_path
        self.config_validator = config_validator
        self.default_conf_file_required = False

    def __call__(self, value):
        new_config = {}
        path_to_config = None if value is None else Path(value)

        if path_to_config is not None:
            try:
                with path_to_config.open() as config_file:
                    new_config = yaml.load(config_file.read())
            except OSError as error:
                raise self.Invalid(str(error))

        elif self.default_path_to_config is not None:
            try:
                with self.default_path_to_config.open() as config_file:
                    new_config = yaml.load(config_file.read())
            except OSError as error:
                if self.default_conf_file_required:
                    raise self.Invalid(str(error))

        try:
            new_config = self.config_validator(new_config)
        except Invalid as error:
            raise self.Invalid(str(error))

        self.config.update(new_config)
