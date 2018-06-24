import random

from asterios.level import BaseLevel, Difficulty


class Level1(BaseLevel):
    """
    ["2 + 3", "5 + 3", ...]  --> [6, 7, ...]
    """

    def __init__(self, difficulty):
        super().__init__(difficulty)
        self.expected = []

    def generate_puzzle(self):
        puzzle = []
        self.expected = []
        for _ in range(500):
            a = random.randint(0, 9)
            b = random.randint(0, 9)

            puzzle.append("{} + {}".format(a, b))
            self.expected.append(a + b)
        return puzzle

    def check_answer(self, answer):
        if answer != self.expected:
            return (False, "Do you know eval ?")
        return (True, "good job")


class Level2(BaseLevel):
    """
    ["a + b", "b + c", ...]  --> [??, ??, ...]
    """

    def __init__(self, difficulty):
        super().__init__(difficulty)
        self.tries = 0
        self.expected = []

    def generate_puzzle(self):
        puzzle = []
        self.expected = []
        for _ in range(500):
            a = random.randint(0, 15)
            b = random.randint(0, 15)
            if self.difficulty is Difficulty.easy:
                puzzle.append("{:x} + {:x}".format(a, b))
                self.expected.append("{:x}".format(a + b))
            else:
                if random.randint(0, 1):
                    puzzle.append("{:x} + {:x}".format(a, b))
                    self.expected.append("{:x}".format(a + b))
                else:
                    puzzle.append("{:x} - {:x}".format(a, b))
                    self.expected.append("{:x}".format(a - b))

        return puzzle

    def check_answer(self, answer):
        is_exact = answer == self.expected
        comment = ":-)"
        if not is_exact:
            if self.tries < 5:
                self.tries += 1
                comment = "I help you later"
            else:
                comment = "a = 10"
        return (is_exact, comment)
