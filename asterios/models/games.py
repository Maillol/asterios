import random

from voluptuous import All, Match, Range, Required, Schema

from .basemodel import Collection, ModelMixin, collection
from .errors import GameConflict, MemberDoesntExist
from .team_members import TeamMember
from .utils import utcnow


CREATE_GAME_VALIDATOR = Schema({
    Required('team'): Match(r'^[-a-zA-Z0-9]+$'),
    Required('team_members'): collection(TeamMember, min_length=1),
    Required('state', default='ready'): 'ready',
    Required('duration'): All(int, Range(min=1)),
})


class _TeamMemberCollection(Collection):

    not_exist_error = MemberDoesntExist

    def generate_id(self, obj):
        id_ = random.randint(1000, 9999)
        obj.id = id_
        return id_


class Game(ModelMixin):

    schema = CREATE_GAME_VALIDATOR

    def __init__(self, team, state, duration, team_members):
        self.team = team
        self.state = state
        self.duration = duration
        self.team_members = _TeamMemberCollection(team_members)
        self.start_at = None
        self.remaining = None

    def set_remaining_time(self):
        """
        Compute the remaining time and set it to the game.
        """
        now = utcnow()
        if self.state == 'start':
            consumption = (now - self.start_at).seconds // 60
            self.remaining = max(self.duration - consumption, 0)
            if self.remaining == 0:
                self.state = 'stop'

    def start(self):
        """
        Start the game. If the game is already started, a GameConflict error
        is raised.
        """
        if self.state == 'start':
            raise GameConflict(
                'The game `{name}` is already started'.format(name=self.team))

        self.state = 'start'
        self.start_at = utcnow()
        self.remaining = self.duration
        return self

    def append_member(self, values: dict):
        """
        Add a new team member to game.
        """
        member = TeamMember.from_dict(values)
        new_id = self.team_members.append(member)
        return self.team_members[new_id]

    def set_question(self, member_id):
        member = self.member_from_id(member_id)
        return member.set_question()

    def check_answer(self, member_id, answer):
        if self.state != 'start':
            raise GameConflict(
                'The game `{name}` is not started'.format(name=self.team))

        member = self.member_from_id(member_id)
        return member.check_answer(answer)

    def member_from_id(self, member_id):
        """
        Get a team member from id or raise MemberDoesntExist exception if
        the team member doesn't exist.
        """
        try:
            member_id = int(member_id)
        except ValueError:
            raise MemberDoesntExist(member_id, field='id')
        return self.team_members[member_id]

    def member_from_name(self, member_name):
        """
        Get a team member from name or raise MemberDoesntExist exception if
        the team member doesn't exist.
        """
        return self.team_members.get_first_from_value('name', member_name)
