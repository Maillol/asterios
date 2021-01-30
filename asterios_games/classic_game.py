from asterios.level import BaseLevel, Difficulty

from copy import deepcopy
import itertools
import random
from textwrap import dedent


class Level1(BaseLevel):
    """
    X?O
    OXX
    ?OO

    Dans les morpions Ni perdant, Ni gagnant
    """

    @staticmethod
    def _has_winer(morpion):
        for i in range(0, 9, 3):
            if morpion[0 + i] == morpion[1 + i] == morpion[2 + i]:
                return True

        for i in range(3):
            if morpion[0 + i] == morpion[3 + i] == morpion[6 + i]:
                return True

        if morpion[0] == morpion[4] == morpion[8]:
            return True

        if morpion[2] == morpion[4] == morpion[6]:
            return True

        return False

    @staticmethod
    def positions(morpion, symbole):
        """
        >>> positions(['X', 'O', 'O', 'X', 'X', 'O', 'O', 'X', 'O'], 'X')
        [0, 3, 4, 7]
        """
        return list(i for i, cell in enumerate(morpion) if cell == symbole)

    def __init__(self, difficulty):
        super().__init__(difficulty)
        possibles = []
        for i in range(9):
            for j in range(9):
                if j != i:
                    for k in range(9):
                        if k not in (i, j):
                            for l in range(9):
                                if l not in (i, j, k):
                                    m = ["O"] * 9
                                    m[i] = "X"
                                    m[j] = "X"
                                    m[k] = "X"
                                    m[l] = "X"
                                    if not self._has_winer(m):
                                        possibles.append(m)

        self.possibles = possibles

    @staticmethod
    def _morpion_to_str(morpion):
        """
        >>> Level1._morpion_to_str(
        ...    ['X', 'O', 'O', 'X', 'X', 'O', 'O', 'X', 'O'])
        'XOO\nXXO\nOXO'
        """
        return "\n".join(
            ("".join(morpion[0:3]), "".join(morpion[3:6]), "".join(morpion[6:9]))
        )

    def generate_puzzle(self):
        solutions = []
        puzzles = []
        for morpion in random.sample(deepcopy(self.possibles), 100):
            solutions.append([self._morpion_to_str(morpion)])

            i_x = random.choice(self.positions(morpion, "X"))
            morpion[i_x] = "?"
            i_o = random.choice(self.positions(morpion, "O"))
            morpion[i_o] = "?"
            puzzles.append(self._morpion_to_str(morpion))

            morpion[i_x] = "O"
            morpion[i_o] = "X"
            if not self._has_winer(morpion):
                solutions[-1].append(self._morpion_to_str(morpion))

        self.solutions = solutions
        return puzzles

    def check_answer(self, answer):
        if len(self.solutions) != len(answer):
            return (False, "Renvoie moi toutes les grilles complétées")

        for expected, completed in zip(self.solutions, answer):
            if completed not in expected:
                return (False, "Je cette grille est mal {}".format(completed))

        return (True, "Félicitation :-)")


class Level2(BaseLevel):
    """
    carré, brelan ?

    2♠ 2♣ 2♥ 2♦ 7♥
    """

    RANKS = ("1", "R", "D", "V", "10", "9", "8", "7", "6", "5", "4", "3", "2")
    SHAPES = "♠♣♥♦"

    HANDS = (
        ("quinte flush royale", "royal flush"),
        ("quinte flush", "straight flush"),
        ("carré", "quads", "four of a kind"),
        ("brelan", "set", "trips", "three of a kind"),
    )

    @classmethod
    def _rank(cls, excludes=()):
        return random.choice([rank for rank in cls.RANKS if rank not in excludes])

    @classmethod
    def _shapes(cls, excludes=()):
        return random.choice([shape for shape in cls.SHAPES if shape not in excludes])

    def _generate_hand(self):
        hand = []
        if self.difficulty is Difficulty.EASY:
            hand_type = random.randint(2, 3)
        else:
            hand_type = random.randint(1, 3)

        if hand_type == 1:  # quinte flush [royale]
            start = random.randint(0, 52)
            j = start % 4
            start //= 4
            shape = self.SHAPES[j]
            if start < 8:
                hand = [rank + shape for rank in self.RANKS[start : start + 5]]
                if start == 0:
                    return (0, hand)
                return (1, hand)

            else:
                hand = [rank + shape for rank in self.RANKS[start - 5 : start]]
                if start == 5:
                    return (0, hand)
                return (1, hand)

        elif hand_type == 2:  #  carré
            rank = self._rank()
            return (
                2,
                [
                    rank + "♠",
                    rank + "♣",
                    rank + "♥",
                    rank + "♦",
                    self._rank((rank,)) + self._shapes(),
                ],
            )

        elif hand_type == 3:  # brelan
            rank = self._rank()
            other_rank_1 = self._rank((rank,))
            other_rank_2 = self._rank((rank, other_rank_1))
            return (
                3,
                [
                    rank + "♠",
                    rank + "♣",
                    rank + "♥",
                    other_rank_1 + self._shapes(),
                    other_rank_2 + self._shapes(),
                ],
            )

    def generate_puzzle(self):
        self.solutions = []
        self.puzzles = []
        for _ in range(100):
            solution, puzzle = self._generate_hand()
            self.solutions.append(solution)
            self.puzzles.append(puzzle)
        return self.puzzles

    def check_answer(self, answer):
        if not isinstance(answer, list):
            return (False, "Donne moi une list")

        if len(answer) != len(self.solutions):
            return (False, "Ta liste n'a pas la bonne taille")

        for i, (s, a) in enumerate(zip(self.solutions, answer)):
            if not isinstance(a, str):
                return (False, "La liste doit contenir des mots")

            if a.lower() not in self.HANDS[s]:
                return (False, "Ceci `{}` n'est pas un `{}`".format(self.puzzles[i], a))

        return (True, ":-)")


class Level3(BaseLevel):
    """
    Ajoute le bloc sans dépasser la dernière ligne.
    """

    # fmt: off
    SHAPES = [
        """
        ▒ 
        ▒▒
        *▒
        """,
        """
         ▒
        ▒▒
        ▒*
        """,
        """
        ▒▒▒
        *▒*
        """,
        """
        ▒ 
        ▒▒
        ▒*
        """,
        """
         ▒
        ▒▒
        *▒
        """,
        """
        ▒▒▒
        **▒
        """,
        """
        ▒▒▒
        ▒**
        """,
        """
        ▒▒
        *▒
        *▒
        """,
        """
        ▒▒
        ▒*
        ▒*
        """
    ]
    # fmt: on

    SHAPES = [
        [list(line) for line in dedent(shape).strip("\n").splitlines()]
        for shape in SHAPES
    ]

    SHAPES_PER_DIFFICULTY = {Difficulty.EASY: 0, Difficulty.NORMAL: 3, Difficulty.HARD: len(SHAPES) - 1}

    @staticmethod
    def paste_shape(canvas, shape, x):
        """
        Paste the shape on the canvas, the '*' chars will be not pasted.

        >>> shape = [
        ...    ['r', ' '],
        ...    ['r', 'r'],
        ...    ['*', 'r']
        ... ]
        >>> canvas = [
        ...    ['a'] * 10,
        ...    ['b'] * 10,
        ...    ['c'] * 10,
        ...    ['d'] * 10
        ... ]
        >>> Level1.paste_shape(canvas, shape, 8) == [
        ... ['a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'r', ' '],
        ... ['b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'r', 'r'],
        ... ['c', 'c', 'c', 'c', 'c', 'c', 'c', 'c', 'c', 'r'],
        ... ['d', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd']]
        True
        >>> canvas = [
        ...    ['a'] * 10,
        ...    ['b'] * 10,
        ...    ['c'] * 10,
        ...    ['d'] * 10
        ... ]
        >>> Level1.paste_shape(canvas, shape, 0) == [
        ... ['r', ' ', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a'],
        ... ['r', 'r', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b'],
        ... ['c', 'r', 'c', 'c', 'c', 'c', 'c', 'c', 'c', 'c'],
        ... ['d', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd']]
        True
        """
        shape_len = len(shape[0])
        for y in range(len(shape)):
            for i_shape, i_canvas in enumerate(range(x, x + shape_len)):
                if shape[y][i_shape] != "*":
                    canvas[y][i_canvas] = shape[y][i_shape]
        return canvas

    @staticmethod
    def add_gaps(canvas, excludes):
        """
        >>> canvas = [
        ...    ['a'] * 10,
        ...    ['b'] * 10,
        ...    ['c'] * 10,
        ...    ['d'] * 10
        ... ]
        >>> _ = Level1.add_gaps(canvas, [-1, 0, 1, 2])
        >>> for y in range(4):
        ...     for i in range(2):
        ...         assert canvas[y][i] != ' '
        """
        for i, j in enumerate(random.sample(set(range(10)) - set(excludes), 4)):
            canvas[i][j] = " "
        return canvas

    def generate_puzzle(self):
        solutions = []
        puzzles = []

        nb_shape = self.SHAPES_PER_DIFFICULTY[self.difficulty]

        def asline(lst):
            return "\n".join("".join(line).center(10) for line in lst)

        for _ in range(100):
            canvas = [["█"] * 10 for _ in range(4)]

            shape = self.SHAPES[random.randint(0, nb_shape)]
            x = random.randint(0, 10 - len(shape[0]))
            excludes = range(x - 1, x + len(shape[0]) + 1)
            self.paste_shape(canvas, shape, x)
            self.add_gaps(canvas, excludes)
            solutions.append(
                self.strip_white_line("\n".join("".join(line) for line in canvas))
            )
            puzzles.append(
                "{}\n{}\n{}".format(
                    asline(shape).replace("*", " "),
                    " " * 10,
                    asline(canvas).replace("▒", " "),
                )
            )
        self.solutions = solutions
        return puzzles

    @staticmethod
    def strip_white_line(text):
        return "".join(line for line in text.splitlines() if not line.isspace())

    def check_answer(self, answer):
        if not isinstance(answer, list):
            return (False, "Donne moi la list de tetris avec le bloc posé")

        if len(self.solutions) != len(answer):
            return (False, "Donne moi tous les tetris avec le bloc posé")

        for expected, completed in zip(self.solutions, answer):
            if not isinstance(completed, str):
                return (
                    False,
                    "Un tetris doit être une chaine de caractères (pas ceci {})".format(
                        completed
                    ),
                )

            if self.strip_white_line(completed) != expected:
                return (False, "Ce tetris n'est pas bon {!r}".format(completed))

        return (True, "Félicitation :-)")


class Level4(BaseLevel):
    """
    Au Mikado, ne perd pas ton tour

        c d    
        │ │    
    a ──│─│────
        │ │         ==>   ["d", "b", "c", "a"]
    b ────│────
        │ │
    """

    LABELS_ORDER = tuple(itertools.permutations(("a", "b", "c", "d")))

    @staticmethod
    def _draw_line(page, num, label):
        if num == 1:
            page[24] = label
            for i in range(26, 35):
                page[i] = "─"
        elif num == 2:
            page[48] = label
            for i in range(50, 59):
                page[i] = "─"
        elif num == 3:
            page[4] = label
            for i in range(16, 76, 12):
                page[i] = "│"
        elif num == 4:
            page[6] = label
            for i in range(18, 78, 12):
                page[i] = "│"

    def _generate_page(self):

        # fmt: off
        page = [
            " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "\n",
            " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "\n",
            " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "\n",
            " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "\n",
            " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "\n",
            " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "]
        # fmt: on

        i_order = random.randint(0, 7)
        order = (
            (1, 3, 2, 4),
            (1, 4, 2, 3),
            (2, 3, 1, 4),
            (2, 4, 1, 3),
            (3, 2, 4, 1),
            (3, 1, 4, 2),
            (4, 2, 3, 1),
            (4, 1, 3, 2),
        )[i_order]

        labels = self.LABELS_ORDER[random.randint(0, 23)]


        if self.difficulty is Difficulty.EASY:
            solution = []
            for i in order:
                label = ' abcd'[i]
                solution.append(label)
                self._draw_line(page, i, label)
        else:
            solution = []
            for label, i in zip(labels, order):
                solution.append(label)
                self._draw_line(page, i, label)

        solution.reverse()
        return solution, "".join(page)

    def generate_puzzle(self):
        self.solutions = []
        puzzles = []
        for _ in range(30):
            solution, puzzle = self._generate_page()
            puzzles.append(puzzle)
            self.solutions.append(solution)
        return puzzles

    def check_answer(self, answer):
        if not isinstance(answer, list):
            return (False, "Donne moi une list")

        if len(answer) != len(self.solutions):
            return (False, "Ta list n'a pas la bonne taille")

        if answer != self.solutions:
            return (False, "Ne tremble pas")

        return (True, ":-)")
