from pathlib import Path

from .config_loader import ArgumentParserBuilder, Required, Optional, Schema
from .config_loader.config_modifiers import YamlConfigInitializerType


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
            msg='level_package_name to load (should be in PYTHONPATH)'): [str],
        Optional(
            'authentication',
            msg='Enable authentication'): {
            'type': 'basic',
            Required('superuser'): {
                Required(
                    'login',
                    msg='The superuser login'): str,
                Required(
                    'password',
                    msg='The superuser password'): str
            }
        }
    }
)


def get_config():
    """
    Try to opens yaml config file and overwirtes it with command line
    parameters.
    """
    argument_parser = ArgumentParserBuilder(schema=_CONFIG_SCHEMA)
    argument_parser.add_config_init(
        '--config-file', 'path to `asterios.yml` configuration file by default,'
        ' file is loaded from current directory',
        YamlConfigInitializerType,
        default_path=Path.cwd() / 'asterios.yml')

    argument_parser.parse_args()
    return argument_parser.config


__all__ = ['get_config']
