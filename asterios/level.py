"""
This module contains class BaseLevel that allow you to
create new Level.

A Level is puzzle generator.

To create a new level, subclasse `BaseLevel` and implement
required method:

The name of subclass should be Level suffixed with number, otherwise
an attribute error is raised

>>> class MyLevel(BaseLevel):
...     pass
Traceback (most recent call last):
...
ValueError: `MyLevel` class name should match "Level[0-9]+"

The class should have docstring the doc string can be a tip to
solve the puzzle.

>>> class Level1(BaseLevel):
...     pass
Traceback (most recent call last):
...
AttributeError: `<class 'level.Level1'>` class shoud define docstring

>>> class Level1(BaseLevel):
...    '''
...    Use eval to compute
...    '''
...    def generate_puzzle(self):
...        self.expected = 7
...        return '3 + 4'
...    def check_answer(self, answer):
...        if answer < self.expected:
...            return 'too small'
...        elif answer == self.expected:
...            return 'too large'
...        return 'Good job'

The MetaLevel.register contains BaseLevel subclasses.
Subclasses are grouped by module in a `theme`

>>> MetaLevel.get_themes()
('level',)
>>> MetaLevel.get_levels('level')
{1: <class 'level.Level1'>}
>>> MetaLevel.get_level('level', 1) is Level1
True
"""

from collections import defaultdict
import importlib
import re


class MetaLevel(type):
    """
    Check level definition
    """

    register = defaultdict(dict)

    def __init__(cls, name, bases, attributes):
        if bases:
            match = re.match('Level(\d+)$', name)
            if match is None:
                raise ValueError(
                    '`{}` class name should match "Level[0-9]+"'.format(cls.__qualname__))
            level = int(match.groups()[0])

            if '__doc__' not in attributes:
                raise AttributeError(
                    '`{}` class shoud define docstring'.format(cls))
            if 'generate_puzzle' not in attributes:
                raise AttributeError(
                    '`{}` class shoud define `generate_puzzle` method'.format(cls))
            if 'check_answer' not in attributes:
                raise AttributeError(
                    '`{}` class shoud define `check_answer` method'.format(cls))

            type(cls).register[cls.__module__][level] = cls

    @classmethod
    def get_level(mcs, theme, level):
        return mcs.register[theme][level]

    @classmethod
    def get_levels(mcs, theme):
        return mcs.register[theme]

    @classmethod
    def get_themes(mcs):
        return tuple(mcs.register)

    @classmethod
    def clean(mcs):
        mcs.register.clear()

    @staticmethod
    def load_level(package):
        importlib.import_module(package)


class BaseLevel(metaclass=MetaLevel):
    """
    Sub-class should define `guide` attribute, `generate_puzzle`
    and `check_answer` methods.
    """

    def generate_puzzle(self):
        """
        Returns a puzzle
        """

    def check_answer(self, answer):
        """
        Returns a 2-tuple The first element should be a True is answer
        is right else False. The second element is a comment.
        """
