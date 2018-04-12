from pathlib import Path

from .config_loader import ArgumentParser, Optional, Schema
from .config_loader.actions import InitFromYamlAction


_CONFIG_SCHEMA = Schema(
    {
        Optional(
            'port',
            default=8080,
            help='Asterio port server'): int,
        Optional(
            'host',
            default='127.0.0.1',
            help='Asterio host server'): str,
        Optional(
            'level_package',
            default=[],
            help='level_package_name to load (should be in PYTHONPATH)'): [str],
    }
)


def get_config():
    """
    Try to opens yaml config file and overwirtes it with command line
    parameters.
    """
    argument_parser = ArgumentParser(schema=_CONFIG_SCHEMA)
    argument_parser.add_config_init(
        '--config-file', 'path to `asterios.yml` configuration file by default,'
        ' file is loaded from current directory',
        InitFromYamlAction,
        default_path=Path.cwd() / 'asterios.yml')

    argument_parser.parse_args()
    return argument_parser.config


__all__ = ['get_config']
