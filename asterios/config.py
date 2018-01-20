import argparse
from pathlib import Path

from voluptuous import Optional, Schema
import yaml

_CONFIG_SCHEMA = Schema(
    {
        Optional(
            'port',
            default=8080,
            msg='Asterio port server'): int,
        Optional(
            'host',
            default='127.0.0.1',
            msg='Asterio host server'): str,
        Optional(
            'level_package',
            default=[],
            msg='level_package_name to load (should be in PYTHONPATH)'): [str]})


NO_OVERWIRTE = object()


def _argument_parser():
    """
    Generate an `ArgumentParser` object from `_CONFIG_SCHEMA`
    module attribute.
    """
    parser = argparse.ArgumentParser(prog='Asterios')
    parser.add_argument('--config-file', type=Path,
                        default=Path.cwd() / 'asterios.yml',
                        help='path to `asterios.yml` configuration file by'
                             ' default, file is loaded from current directory')
    for key, value in _CONFIG_SCHEMA.schema.items():
        if isinstance(value, list):
            type_ = value[0]
            action = 'append'
            default = []
        else:
            type_ = value
            action = 'store'
            default = NO_OVERWIRTE
        parser.add_argument('--{}'.format(key).replace('_', '-'),
                            action=action,
                            default=default,
                            type=type_,
                            help=key.msg)
    return parser


def get_config():
    """
    Try to opens yaml config file and overwirtes it with command line
    parameters.
    """
    args = _argument_parser().parse_args()
    if args.config_file.exists():
        with args.config_file.open() as config_file:
            config = yaml.load(config_file.read())
    else:
        config = {}

    config = _CONFIG_SCHEMA(config)
    config.update(
        {k: v for k, v in vars(args).items()
         if v is not NO_OVERWIRTE and v != [] and k != 'config_file'})

    return config


__all__ = ['get_config']
