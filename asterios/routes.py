"""
This module contains code to bind http handers to a http route.
"""

from .views import GameConfigItemView, GameConfigCollectionView, AsteriosActionPuzzleView, AsteriosActionSolveView, \
    AsteriosItemView, GameConfigActionStartView, GameConfigActionAddMemberView


def setup_routes(app):
    """
    Bind all asterios view with routes.
    """
    app.router.add_view('/asterios/{team}/member/{team_member}', AsteriosItemView, name='asterios-item')
    app.router.add_view('/asterios/{team}/member/{team_member}/puzzle', AsteriosActionPuzzleView, name='asterios-puzzle')
    app.router.add_view('/asterios/{team}/member/{team_member}/solve', AsteriosActionSolveView, name='asterios-solve')
    app.router.add_view('/game-config', GameConfigCollectionView, name='game-collection')
    app.router.add_view('/game-config/{name}', GameConfigItemView, name='game-item')
    app.router.add_view('/game-config/{name}/start', GameConfigActionStartView, name='game-action-start')
    app.router.add_view('/game-config/{name}/add-member', GameConfigActionAddMemberView, name='game-action-add-member')
