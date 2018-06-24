"""
This module contains the class BaseLevel that allow you to create new Level.
A Level is puzzle generator.

To create a new level, subclasse `BaseLevel` and implement required methods
"""

from collections import defaultdict
import enum
import importlib
import re
import textwrap

import attr


def _default(cls, attr_name):
    return next(attribute.default
                for attribute
                in attr.fields(cls)
                if attribute.name == attr_name)


class Difficulty(enum.Enum):
    EASY = 'easy'
    NORMAL = 'normal'
    HARD = 'hard'


class MetaLevel(type):
    """
    Checks level definition and stores BaseLevel subclasses.

    You can call `clean` method to clear the stored subclasses.
    >>> MetaLevel.clean()

    The name of subclass should be Level suffixed with number, otherwise
    an attribute error is raised

    >>> class MyLevel(BaseLevel):
    ...     pass
    Traceback (most recent call last):
    ...
    ValueError: `MyLevel` class name should match "Level[0-9]+"

    The class should have docstring the docstring can be a tip to
    solve the puzzle.

    >>> class Level1(BaseLevel):
    ...     pass
    Traceback (most recent call last):
    ...
    AttributeError: `<class 'asterios.level.Level1'>` class shoud define docstring

    >>> class Level1(BaseLevel):
    ...    \"\"\"
    ...    Use eval to compute
    ...    \"\"\"
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
    ('asterios.level',)
    >>> MetaLevel.get_levels('asterios.level')
    {1: <class 'asterios.level.Level1'>}
    >>> MetaLevel.get_level('asterios.level', 1) is Level1
    True
    """

    register = defaultdict(dict)

    def __init__(cls, name, bases, attributes):
        super().__init__(name, bases, attributes)
        if bases:
            match = re.match(r'Level(\d+)$', name)
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
    def get_level(mcs, theme: str, level: int):
        """
        Return a Level class.
        """
        return mcs.get_levels(theme)[level]

    @classmethod
    def get_levels(mcs, theme: str):
        """
        Return levels loaded in register with theme `theme`.
        """
        if theme not in mcs.register:
            raise LookupError(
                'The theme {!r} is not in the register'.format(theme))
        return mcs.register[theme]

    @classmethod
    def get_themes(mcs):
        """
        Return list of existing `theme` stored in register.
        """
        return tuple(mcs.register)

    @classmethod
    def clean(mcs):
        """
        Remove all level loaded in register.
        """
        mcs.register.clear()

    @staticmethod
    def load_level(package_name: str):
        """
        Load levels from `package_name`
        """
        importlib.import_module(package_name)


class BaseLevel(metaclass=MetaLevel):
    """
    Asterio groups the levels by module name. The levels in the module should be named
    from `Level1` to `LevelN`. Each level is a BaseLevel subclass and redefines two methods.
    `generate_puzzle` and `check_answer`. The docstring of level count. This is a tip to
    resolve the puzzle send to users.

    Example, you can create a class that send a list to sort::

        import random

        from asterios.level import BaseLevel, Difficulty

        class Level1(BaseLevel):
            \"\"\"
            help(list.sort) ;-)
            \"\"\"

            def generate_puzzle(self):
                puzzle = list(range(200))
                self.expected = list(range(200))
                random.shuffle(puzzle)
                return puzzle

            def check_answer(self, answer):
                if answer == self.expected:
                    return (True, 'Good job :-D')
                if not isinstance(answer, list):
                    return (False, 'You should send me a list')
                if len(answer) != len(self.expected):
                    return (False, 'The list should have {} elements'.
                                   format(len(self.expected)))

                return (False, 'Send me a sorted list')

    When a BaseLevel subclass is instantiate, the `difficulty` parameters is provided.
    The difficulty value is a `level.Difficulty` member.
    """
    def __init__(self, difficulty):
        self.difficulty = difficulty

    def generate_puzzle(self):
        """
        This method returns a puzzle to resolve. A puzzle is any jsonifiable data stucture.
        """

    def check_answer(self, answer):
        """
        Returns a 2-tuple The first element should be a True is answer
        is right else False. The second element is a comment.
        """


@attr.s
class LevelSet:
    """
    LevelSet objet allow you to store levels.
        >>> from unittest.mock import Mock
        >>> level1 = Mock(name='Level1()')
        >>> level1.check_answer.return_value = (True, '')
        >>> level2 = Mock(name='Level1()')
        >>> level2.check_answer.return_value = (True, '')

        >>> levels = LevelSet('theme 1', [level1, level2])

    The generate_puzzle method calls generate_puzzle on the current level.
        >>> puzzle = levels.generate_puzzle()
        >>> puzzle is level1.generate_puzzle()
        True

    The check_answer method calls check_answer on the current level.
        >>> levels.check_answer(123)
        (True, '')
        >>> level1.check_answer.assert_called_with(123)
        >>> levels.done
        False

    If check_answer return True, the current level is the next level.
        >>> levels.generate_puzzle() is level2.generate_puzzle()
        True

    You can get the current level number.
        >>> levels.level_number
        2

    When we resove the last level `done` is True
        >>> levels.check_answer(456)
        (True, '')
        >>> level2.check_answer.assert_called_with(456)
        >>> levels.done
        True

    We cannot call `generate_puzzle` when the LevelSet is done.
        >>> levels.generate_puzzle()
        Traceback (most recent call last):
            ...
        asterios.level.LevelSet.DoneException: LevelSet is done
    """

    class DoneException(Exception):
        """
        Raised when all levels in LevelSet are done.
        """

    theme = attr.ib()
    _levels = attr.ib(default=attr.Factory(list))
    _current_level = attr.ib(default=1)
    _level_max = attr.ib()
    _done = attr.ib(init=False, default=False)

    @_level_max.default
    def __len__(self):
        return len(self._levels)

    def generate_puzzle(self):
        """
        Call `generate_puzzle` method on the current level.
        """
        return self.current_level.generate_puzzle()

    def check_answer(self, answer):
        """
        Call `check_answer` method on the current level, if the level is True,
        The next level begin the current level.
        """
        is_exact, comment = self.current_level.check_answer(answer)
        if is_exact:
            if self._current_level < min(len(self._levels), self._level_max):
                self._current_level += 1
            else:
                self._done = True
        return is_exact, comment

    def tip(self):
        """
        Return docstring of current level.
        """
        return textwrap.dedent(self.current_level.__doc__).strip()

    @property
    def done(self):
        """
        Returns True if the LevelSet is done else False.
        """
        return self._done

    @property
    def current_level(self):
        """
        Returns the current level object or raises a DoneException
        """
        if self._done:
            raise self.DoneException('LevelSet is done')
        return self._levels[self._current_level - 1]

    @property
    def level_number(self):
        """
        Return the current level number.
        """
        return self._current_level


def get_level_set(theme, start_level=None, level_max=None,
                  difficulty=Difficulty.NORMAL):
    """
    Return a LevelSet object.
    """
    levels = MetaLevel.get_levels(theme)
    level_set_attribute = {}
    if start_level is not None:
        level_set_attribute['current_level'] = start_level
    if level_max is not None:
        level_set_attribute['level_max'] = level_max

    return LevelSet(
        theme,
        [levels[i](difficulty) for i in range(1, len(levels) + 1)],
        **level_set_attribute
    )


def get_themes():
    """
    Return existing themes of levels stored in register.
    """
    return MetaLevel.get_themes()
