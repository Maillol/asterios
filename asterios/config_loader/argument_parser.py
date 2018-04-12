"""
This module provides `ArgumentParser` class to load a configuration file and
update the loaded configuration using command line arguments.
"""

from argparse import ArgumentParser as _ArgumentParser, ArgumentTypeError, ArgumentError
import sys

from voluptuous import Schema, Invalid

from .config_modifiers import ConfigUpdaterType


def _argument_from_voluptuous(schema):
    """
    Generates a list of 3-tuples from `schema` containing:
        - argument_name
        - dest
        - help

    >>> from asterios.config_loader import Optional, Required
    >>> validator = Schema({
    ...    Optional('port', help='Specify alternate port'): int
    ... })
    >>> _argument_from_voluptuous(validator.schema)
    [('--port', [(<class 'int'>, 'port')], 'Specify alternate port')]

    >>> validator = Schema({
    ...    Optional('user', help='user'): {
    ...         Required('name', help='The user name'): str,
    ...         'last_name': str}
    ... })
    >>> args = _argument_from_voluptuous(validator.schema)
    >>> ('--user-name',
    ...  [(dict, 'user'), (str, 'name')], 'The user name') in args
    True
    >>> ('--user-last-name',
    ...  [(dict, 'user'), (str, 'last_name')], 'user') in args
    True

    >>> validator = Schema({
    ...    Optional('modules'): [str]
    ... })
    >>> _argument_from_voluptuous(validator.schema)
    [('--modules', [(<class 'list'>, 'modules'), (<class 'str'>, None)], '')]


    >>> validator = Schema({
    ...     Optional('users'): [{
    ...         Optional('friends'): [{Required('name'): str}]
    ...     }]
    ... })
    >>> args = _argument_from_voluptuous(validator.schema)
    >>> args == [
    ...     ('--users-friends-name',
    ...      [(list, 'users'), (dict, None), (list, 'friends'),
    ...       (dict, None), (str, 'name')], '')]
    True
    """

    arguments = []

    def _route(key, value, dest, key_help):

        key_name = None if key is None else str(key)
        key_help = key.help if getattr(key, 'help', '') else key_help

        if isinstance(value, dict):
            for key, value in value.items():  # pylint: disable=R1704
                _route(key, value,
                       dest + [(dict, key_name)],
                       key_help)

        elif isinstance(value, list):
            for item in value:
                _route(None, item,
                       dest + [(list, key_name)],
                       key_help)

        else:
            dest.append((value, key_name))
            dest = dest[1:]

            param = '-'.join(key_name
                             for _, key_name
                             in dest
                             if key_name is not None).replace('_', '-')

            arguments.append(('--{}'.format(param), dest, key_help))

    _route(None, schema, [], '')
    return arguments


class ArgumentParserBuilder:
    """
    Build an argparse.ArgumentParser object dedicated to load
    configuration.

        prog - the name of the program (default: sys.argv[0])
        description - a short description of program (default: '')
        schema - A voluptuous schema used to validate the configuration
                 file and generate argument to update the loaded
                 configuration.
    """

    def __init__(self, prog=sys.argv[0], description='', schema=None):
        self._argument_parser = _ArgumentParser(
            prog=prog, description=description)
        self._config = {}
        self._schema = Schema({}) if schema is None else schema
        for arg, dest, help_ in _argument_from_voluptuous(self._schema.schema):
            self.add_config_updater(arg, help_, dest=dest)

    @property
    def config(self):
        """
        Returns the configuration
        """
        return self._config.copy()

    @property
    def args(self):
        """
        Returns the parsed arguments.
        """
        return self._args

    @property
    def argument_parser(self):
        """
        Returns the argument_parser
        """
        return self._argument_parser

    def add_config_updater(self, argument_name, argument_help, dest):
        """
        Binds ConfigUpdater to an argument.
        """
        self._argument_parser.add_argument(
            argument_name,
            metavar=argument_name.split('-')[-1].upper(),
            help=argument_help,
            action='append',
            type=ConfigUpdaterType(self._config, dest),
            dest='update_actions',
            default=[]
        )

    def add_config_init(self, argument_name, argument_help,
                        action_class, default_path=None,
                        default_is_required=False):

        config_initializer_type = action_class(
            self._config, self._schema, default_path, default_is_required)

        self._argument_parser.add_argument(
            argument_name,
            metavar='FILE',
            help=argument_help,
            action='store',
            type=config_initializer_type,
            dest='init_action',
            default=config_initializer_type
        )

    def parse_args(self, args=None):
        """
        Builds the configuration parsing the command line arguments 
        and returns it
        """
        args = self._argument_parser.parse_args(args)
        if hasattr(args, 'init_action'):
            try:
                args.init_action.modify_config()
            except (ArgumentError, ArgumentTypeError) as error:
                self._argument_parser.error(str(error))
            delattr(args, 'init_action')

        for action in args.update_actions:
            try:
                action.modify_config()
            except (ArgumentError, ArgumentTypeError) as error:
                self._argument_parser.error(str(error))
        delattr(args, 'update_actions')

        self._args = args

        try:
            self._config = self._schema(self._config)
        except Invalid as error:
            print(str(error), file=sys.stderr)
            exit(2)
        return self._config
