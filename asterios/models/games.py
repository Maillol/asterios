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
        if self.state == 'started':
            consumption = (now - self.start_at).seconds // 60
            self.remaining = max(self.duration - consumption, 0)
            if self.remaining == 0:
                self.state = 'stopped'

    def start(self):
        """
        Start the game. If the game is already started, a GameConflict error
        is raised.
        """
        self.ensure_state_is_not('started')
        self.state = 'started'
        self.start_at = utcnow()
        self.remaining = self.duration
        return self

    def add_member(self, values: dict):
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
        self.ensure_state_is('started')
        member = self.member_from_id(member_id)
        return member.check_answer(answer)

    def ensure_state_is(self, state:str):
        """
        Ensure that game state is `state` or raise a GameConflict exception.
        """
        if self.state != state:
            raise GameConflict(
                'The game `{name}` is not {state}'.format(name=self.team, state=state))

    def ensure_state_is_not(self, state:str):
        """
        Ensure that game state is not `state` or raise a GameConflict exception.
        """
        if self.state == state:
            raise GameConflict(
                'The game `{name}` is already {state}'.format(name=self.team, state=state))

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
