from asterios.config_loader import Schema, Optional, Required
from asterios.config_loader.argument_parser import ArgumentParserBuilder

import unittest
from unittest import mock
from io import StringIO
import sys


_CONFIG_SCHEMA = Schema(
    {
        # Scalar
        Optional(
            'port',
            default=8080,
            msg='port server'): int,

        # List of scalar
        Optional(
            'plugins',
            default=[],
            msg='plugins to load'): [str],

        # List of dict
        Optional(
            'users',
            default=[],
            msg='plugins to load'): [{
                Required(
                    'login',
                    msg='The superuser login'): str,
                Required(
                    'password',
                    msg='The superuser password'): str
            }],

        # Dict of dict
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


class TestArgumentParserBuilder(unittest.TestCase):

    def setUp(self):
        self.argument_parser = ArgumentParserBuilder(schema=_CONFIG_SCHEMA)


class TestDefaultArgs(TestArgumentParserBuilder):

    def setUp(self):
        super().setUp()
        self.config = self.argument_parser.parse_args([])

    def test_port_should_be_set_to_default_value(self):
        self.assertEqual(self.config['port'], 8080)

    def test_plugins_should_be_set_with_an_empty_list(self):
        self.assertEqual(self.config['plugins'], [])

    def test_users_should_be_set_with_an_empty_list(self):
        self.assertEqual(self.config['users'], [])

    def test_authentication_should_be_unset(self):
        self.assertNotIn('authentication', self.config)


class TestSetPort(TestArgumentParserBuilder):
    def test_port_should_contain_given_value(self):
        config = self.argument_parser.parse_args(['--port', '80'])
        self.assertEqual(config['port'], 80)

    def test_parser_should_exit_when_set_port_with_wrong_value(self):
        stderr = StringIO()
        with mock.patch.object(sys, 'stderr', stderr):
            with self.assertRaises(SystemExit):
                config = self.argument_parser.parse_args(['--port', 'ff'])

        self.assertIn(
            "--port: invalid literal for int() with base 10: 'ff'",
            stderr.getvalue())


class TestSetPlugins(TestArgumentParserBuilder):
    def test_plugins_should_contain_loglib_and_syslib(self):
        config = self.argument_parser.parse_args(
            ['--plugins', 'loglib', '--plugins', 'syslib'])

        self.assertEqual(config['plugins'], ['loglib', 'syslib'])


class TestSetUsers(TestArgumentParserBuilder):

    @unittest.skip('Not implemented')
    def test_users_should_contain_two_dicts_with_login_and_password(self):
        config = self.argument_parser.parse_args(
            ['--users-login', 'user1', '--users-password', 'pwd1',
             '--users-login', 'user2', '--users-password', 'pwd2'])

        self.assertEqual(config['users'],
                         [{'login': 'user1',
                           'password': 'pwd1'},
                          {'login': 'user2',
                           'password': 'pwd2'}])


class TestSetAuthentication(TestArgumentParserBuilder):

    def test_authentication_and_superuser_should_be_set(self):
        config = self.argument_parser.parse_args(
            ['--authentication-type', 'basic',
             '--authentication-superuser-login', 'super_user',
             '--authentication-superuser-password', 'super_pwd'])

        self.assertEqual(config['authentication'],
                         {'type': 'basic',
                          'superuser': {
                              'login': 'super_user',
                              'password': 'super_pwd'
                          }})

    def test_parser_should_exit_when_set_authentication_type_with_wrong_value(self):
        stderr = StringIO()
        with mock.patch.object(sys, 'stderr', stderr):
            with self.assertRaises(SystemExit):
                config = self.argument_parser.parse_args(
                    ['--authentication-type', 'auth1'])

        self.assertIn(
            "error: argument --authentication-type:"
            " 'basic' is expected (got 'auth1')",
            stderr.getvalue())

    def test_parser_should_exit_when_set_authentication_without_superuser(self):
        stderr = StringIO()
        with mock.patch.object(sys, 'stderr', stderr):
            with self.assertRaises(SystemExit):
                config = self.argument_parser.parse_args(
                    ['--authentication-type', 'basic'])

        # This error cannot be provided by argparse https://bugs.python.org/issue11588
        self.assertIn(
            "required key not provided @ data['authentication']['superuser']",
            stderr.getvalue())
