from .basemodel import Collection
from .errors import GameConflict, GameDoesntExist, error_middleware
from .games import Game
from .team_members import TeamMember


class _GameCollection(Collection):

    not_exist_error = GameDoesntExist

    def generate_id(self, obj):
        id_ = obj.team
        if self.has_id(id_):
            raise GameConflict(
                'The game with name `{name}` already exists'.format(name=id_))
        return id_


class Model:

    def __init__(self):
        self._games = _GameCollection()

    def create(self, game):
        game = Game.from_dict(game)
        self._games.append(game)
        return game

    def game(self, name):
        """
        Return a game
        """
        game = self._games[name]
        game.set_remaining_time()
        return game

    def __iter__(self):
        for game in self._games:
            game.set_remaining_time()
            yield game

    def games(self):
        """
        Return all games
        """
        return list(self)

    def delete_game(self, name):
        """
        delete a game
        """
        self._games.delete(name)

    def start(self, name):
        game = self.game(name)
        game.start()
        return game

    def drop(self):
        self._games.clear()

    def set_question(self, game_name, member_id):
        member = self.member_from_id(game_name, member_id)
        return member.set_question()

    def check_answer(self, game_name, member_id, answer):
        game = self.game(game_name)
        return game.check_answer(member_id, answer)

    def member_from_id(self, game_name, member_id):
        game = self.game(game_name)
        return game.member_from_id(member_id)

    def member_from_name(self, game_name, member_name):
        game = self.game(game_name)
        return game.member_from_name(member_name)
