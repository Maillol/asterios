from asterios.level import BaseLevel, Difficulty

import random


class Level1(BaseLevel):
    """
    ┌┬┬┐
    ││││
    │  │    ['gauche', 'haut', 'gauche', 'gauche', 'bas',
     ││ ←    'gauche']
    ││││
    └┴┴┘

    ┌─── ┐
    ├─ ──┤   ['haut', 'droite', 'droite', 'haut', '?',
    ├── ─┤    '?', '?', '?', '?']
    └ ───┘
     ↑
    """

    def __init__(self, difficulty):
        super().__init__(difficulty)
        self.solutions = object()

    @staticmethod
    def horizontal(direction):

        l = [[' ', '┌', '┬', '┬', '┐', ' '],
             [' ', '│', '│', '│', '│', ' '],
             [' ', '│', '│', '│', '│', ' '],
             [' ', '│', '│', '│', '│', ' '],
             [' ', '│', '│', '│', '│', ' '],
             [' ', '└', '┴', '┴', '┘', ' ']]

        positions = []
        dore_position = random.randint(1, 4)

        if direction == 'droite':
            l[dore_position][0] = '→'
            l[dore_position][1] = ' '
            wall_without_door = range(2, 5)
        else:
            l[dore_position][-1] = '←'
            l[dore_position][-2] = ' '
            wall_without_door = range(-3, -6, -1)

        positions.append(dore_position)

        for i in wall_without_door:
            dore_position = random.randint(1, 4)
            l[dore_position][i] = ' '
            positions.append(dore_position)

        solution = [direction]
        for i, j in zip(positions[1:], positions):
            x = i - j
            if x < 0:
                for _ in range(-x):
                    solution.append('haut')
            elif x > 0:
                for _ in range(x):
                    solution.append('bas')
            solution.append(direction)

        return ('\n'.join(''.join(e) for e in l), solution)

    @staticmethod
    def vertical(direction):

        l = [[' ', ' ', ' ', ' ', ' ', ' '],
             ['┌', '─', '─', '─', '─', '┐'],
             ['├', '─', '─', '─', '─', '┤'],
             ['├', '─', '─', '─', '─', '┤'],
             ['└', '─', '─', '─', '─', '┘'],
             [' ', ' ', ' ', ' ', ' ', ' ']]

        positions = []
        dore_position = random.randint(1, 4)

        if direction == 'bas':
            l[0][dore_position] = '↓'
            l[1][dore_position] = ' '
            wall_without_door = range(2, 5)
        else:
            l[-1][dore_position] = '↑'
            l[-2][dore_position] = ' '
            wall_without_door = range(-3, -6, -1)

        positions.append(dore_position)

        for i in wall_without_door:
            dore_position = random.randint(1, 4)
            l[i][dore_position] = ' '
            positions.append(dore_position)

        solution = [direction]

        for i, j in zip(positions[1:], positions):
            x = i - j
            if x < 0:
                for _ in range(-x):
                    solution.append('gauche')
            elif x > 0:
                for _ in range(x):
                    solution.append('droite')
            solution.append(direction)

        return ('\n'.join(''.join(e) for e in l), solution)

    def generate_puzzle(self):
        puzzles = []
        self.solutions = []
        for _ in range(100):
            if self.difficulty is Difficulty.EASY:
                direction = 0
            elif self.difficulty is Difficulty.NORMAL:
                direction = random.randint(0, 1)
            else:
                direction = random.randint(0, 3)

            if direction < 2:
                puzzle, solution = self.vertical(
                    ('bas', 'haut')[direction % 2])
            else:
                puzzle, solution = self.horizontal(
                    ('gauche', 'droite')[direction % 2])

            self.solutions.append(solution)
            puzzles.append(puzzle)
        return puzzles

    def check_answer(self, answer):
        if answer == self.solutions:
            return (True, 'Bravo :-)')

        if not isinstance(answer, list):
            return (False, 'Passe moi une liste')

        if not all(isinstance(e, list) for e in answer):
            return (False, 'Passe moi une liste de liste')

        return (False, ':-/')


class Level2(BaseLevel):
    """
    ┌─┌┐
    └─┘│
     o─┘

    ['droite', 'droite', 'haut', 'haut', 'gauche',
     'bas', 'gauche', 'gauche', 'haut', 'droite']
    """

    MAX = 5

    def __init__(self, difficulty):
        super().__init__(difficulty)
        self.solutions = object()

    @classmethod
    def _draw_next_step(cls, matrix, start, path):
        """
        Draw a next part of path on the matrix.
        this function return None if it cannot draw.

        Return the postion of added part.
        The direction is added in path
        """

        directions = ['droite', 'bas', 'gauche', 'haut']

        if start[0] == 0:
            directions.remove('gauche')
        elif start[0] == cls.MAX - 1:
            directions.remove('droite')

        if start[1] == 0:
            directions.remove('haut')
        elif start[1] == cls.MAX - 1:
            directions.remove('bas')

        random.shuffle(directions)
        for direction in directions:
            if direction == 'droite':
                p = (start[0] + 1, start[1])
                if matrix[p] != ' ' or matrix.get((start[0] + 2, start[1])) == 'o':
                    continue

                matrix[p] = '─'
                if matrix[start] == '│':
                    if path[-1] == 'haut':
                        matrix[start] = '┌'
                    elif path[-1] == 'bas':
                        matrix[start] = '└'
                path.append('droite')

            elif direction == 'bas':
                p = (start[0], start[1] + 1)
                if matrix[p] != ' ' or matrix.get((start[0], start[1] + 2)) == 'o':
                    continue

                matrix[p] = '│'
                if matrix[start] == '─':
                    if path[-1] == 'gauche':
                        matrix[start] = '┌'
                    elif path[-1] == 'droite':
                        matrix[start] = '┐'

                path.append('bas')

            elif direction == 'gauche':
                p = (start[0] - 1, start[1])
                if matrix[p] != ' ' or matrix.get((start[0] - 2, start[1])) == 'o':
                    continue

                matrix[p] = '─'
                if matrix[start] == '│':
                    if path[-1] == 'haut':
                        matrix[start] = '┐'
                    elif path[-1] == 'bas':
                        matrix[start] = '┘'
                path.append('gauche')

            else:  # direction == 'UP'
                p = (start[0], start[1] - 1)
                if matrix[p] != ' ' or matrix.get((start[0], start[1] - 2)) == 'o':
                    continue

                matrix[p] = '│'
                if matrix[start] == '─':
                    if path[-1] == 'gauche':
                        matrix[start] = '└'
                    elif path[-1] == 'droite':
                        matrix[start] = '┘'

                path.append('haut')

            return p
        return None

    def generate_puzzle(self):

        puzzles = []
        self.solutions = []
        for _ in range(100):
            matrix = Matrix(self.MAX, self.MAX)
            solution = []
            point = (2, 2)
            matrix[point] = 'o'

            try:
                while True:
                    point = self._draw_next_step(matrix, point, solution)
                    if point is None:
                        break
            except IndexError:
                pass

            self.solutions.append(solution)
            puzzles.append(str(matrix))

        return puzzles

    def check_answer(self, answer):
        if answer == self.solutions:
            return (True, 'Bien joué !')

        if not isinstance(answer, list):
            return (False, 'Passe moi une liste')

        if not all(isinstance(e, list) for e in answer):
            return (False, 'Passe moi une liste de liste')

        return (False, ':-/')


class Level3(BaseLevel):
    """
    Quel est le chemin le plus rapide ...
    {
        'start': 8,     #  En partant de la clé start
        8: [3, 4, 8],   #  indique moi la bonne bifurcation
        4: 7,           #  évite les impasses
        7: 'end'        #  et va jusqu'au `end`
    }                   #  Pour cet example le plan est:
                        #  [8, 4, 7]
    """

    random.randint(0, 100)

    @staticmethod
    def _add_loops(path, d, unused):
        for i in range(5, len(path), 5):
            j = i - random.randint(0, 3)
            k = d[path[i]]
            choice = [k, path[j], unused.pop()]
            random.shuffle(choice)
            d[path[i]] = choice

    def generate_puzzle(self):
        path = []
        previous = 'start'
        d = {}
        used = [str(i) for i in random.sample(range(0, 5000), 1000)]
        unused = used[:200]

        for i in used[200:]:
            path.append(i)
            d[previous] = i
            previous = i
        d[previous] = 'end'

        self._add_loops(path, d, unused)
        self.solution = path
        return d

    def check_answer(self, answer):
        if answer == self.solution:
            return (True, 'Bien joué !')

        if not isinstance(answer, list):
            return (False, 'Passe moi une liste')

        return (False, "Tu t'es perdu :-/")


class Matrix:
    """
    >>> m = Matrix(2, 2)
    >>> str(m)
    '  \\n  '
    >>> m[(0, 0)] = 'A'
    >>> m[(1, 0)] = 'B'
    >>> m[(1, 1)] = 'D'
    >>> str(m)
    'AB\\n D'
    """

    def __init__(self, hight, length):
        self.matrice = []
        for _ in range(hight):
            self.matrice.append([' '] * length)

    def __getitem__(self, point):
        if point[1] < 0 or point[0] < 0:
            raise IndexError('[({}, {})]'.format(*point))
        return self.matrice[point[1]][point[0]]

    def get(self, point):
        try:
            return self[point]
        except IndexError:
            return ' '

    def __setitem__(self, point, value):
        self.matrice[point[1]][point[0]] = value

    def __str__(self):
        return '\n'.join((''.join(line) for line in self.matrice))
