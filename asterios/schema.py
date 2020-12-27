import datetime

from pydantic import BaseModel, Field
from typing import Optional, List

from asterios.level import Difficulty


class LevelSchema(BaseModel):
    """
    The current level of game that are playing by a team member.
    """

    theme: str = Field(description="The current level")
    level: int = Field(description="The current theme")


class TeamMemberCreationSchema(BaseModel):
    """
    The parameters to create a new team member.
    """

    name: str = Field(description="The name of the team member")
    level: int = Field(default=1, description="The starting level")
    theme: Optional[str] = Field(
        default=None,
        description="The theme of set of puzzle."
        " It will be randomly chosen if is it not set by the user.",
    )
    level_max: Optional[int] = Field(default=None, description="The last level.")
    difficulty: Difficulty = Field(
        default=Difficulty.EASY, description="The difficulty of set of puzzle."
    )


class ReturnedTeamMemberSchema(TeamMemberCreationSchema):
    """
    After creation, the Team Member object embed a levels_obj containing data about the current level.
    """

    levels_obj: LevelSchema


class GameCreationSchema(BaseModel):
    """
    The parameters to create a Game object.
    """

    team: str = Field(description="The name of team")
    team_members: List[TeamMemberCreationSchema]
    duration: int = Field(default=1, description="The game duration in minute")

    class Config:
        schema_extra = {
            "example": {
                "team": "team-17",
                "team_members": [{"name": "Toto"}],
                "duration": 10,
            }
        }


class ReturnedGameSchema(GameCreationSchema):
    """
    The returned Game.
    """

    state: str = Field(
        description='The state of game can be "ready", "started" or "stopped"'
    )
    start_at: datetime.datetime = Field(description="The starting date")
    remaining: int = Field(description="The remaining time in minute")
    won_at: datetime.datetime = Field(
        description="The date of victory in ISO 8601 format"
    )

    class Config:
        schema_extra = {
            "example": {
                "team": "team-17",
                "team_members": [
                    {
                        "name": "Toto",
                        "id": 2013,
                        "levels_obj": {"level": 2, "theme": "laby"},
                        "level": 1,
                        "level_max": 2,
                    }
                ],
                "duration": 10,
                "state": "ready",
            }
        }


class ErrorSchema(BaseModel):
    message: str
    exception: str
