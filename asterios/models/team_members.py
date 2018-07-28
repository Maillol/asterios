import random

from voluptuous import All, Any, Invalid, Range, Required, Schema

from ..level import Difficulty, get_level_set, get_themes
from .basemodel import ModelMixin
from .utils import utcnow


def difficulty_validator(value):
    """
    Check if value is a valid difficulty.
    """
    try:
        return Difficulty(value)
    except ValueError:
        expected_values = tuple(member.value for member in Difficulty)
        raise Invalid('Value should be one of: {}'.format(expected_values))



CREATE_TEAM_MEMBER_VALIDATOR = Schema({
    Required('name'): str,
    Required('level', default=1): All(int, Range(min=1)),
    Required('theme', default=''): str,
    Required('level_max', default=None): Any(None, All(int, Range(min=1))),
    Required('difficulty', default=Difficulty.EASY): difficulty_validator
})


class TeamMember(ModelMixin):

    schema = CREATE_TEAM_MEMBER_VALIDATOR

    def __init__(self, name, level, level_max, theme, difficulty):
        self.name = name
        self.level = level
        self.level_max = level_max
        self.theme = theme
        self.difficulty = difficulty
        self.levels_obj = None
        self.won_at = None
        self.build_level_set()


    def set_question(self):
        """
        Return the current puzzle to resolve.
        """
        level_set = self.levels_obj
        return {
            'puzzle': level_set.generate_puzzle(),
            'tip': level_set.tip(),
        }

    def check_answer(self, answer):
        """
        Check if the answer resolve the current puzzle.
        """
        level_set = self.levels_obj
        is_exact, comment = level_set.check_answer(answer)
        if is_exact:
            if level_set.done:
                self.won_at = utcnow()
            else:
                self.set_question()
        return is_exact, comment

    def build_level_set(self):
        """
        Build a `LevelSet` object using `theme` attribute and set to
        the `levels_obj` attribute.

        The `theme` of built `LevelSet` will be chosen randomly if the expected
        theme is not found or empty.
        """
        themes = get_themes()
        theme = self.theme
        difficulty = self.difficulty
        if theme not in themes:
            theme = random.choice(themes)
        self.levels_obj = get_level_set(theme,
                                        self.level,
                                        self.level_max,
                                        difficulty)
