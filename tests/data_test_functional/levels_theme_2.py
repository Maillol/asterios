from asterios.level import BaseLevel, Difficulty


class Level1(BaseLevel):
    """
    Fake Level 2.1 tip
    """

    def generate_puzzle(self):
        if self.difficulty is Difficulty.EASY:
            return 'fake generated puzzle 2.1 (easy)'
        elif self.difficulty is Difficulty.NORMAL:
            return 'fake generated puzzle 2.1 (normal)'
        elif self.difficulty is Difficulty.HARD:
            return 'fake generated puzzle 2.1 (hard)'

    def check_answer(self, answer):
        if answer == 'right answer':
            return (True, 'Go to level 2.2')
        return (False, answer)


class Level2(BaseLevel):
    """
    Fake Level 2.2 tip
    """

    def generate_puzzle(self):
        return 'fake generated puzzle 2.2'

    def check_answer(self, answer):
        if answer == 'right answer':
            return (True, 'Finish levels_theme_2')
        return (False, answer)

