from .views import AsteriosView, GameConfig


def setup_routes(app):
    app.router.add_route(
        '*', '/game-config/{name}', GameConfig, name='game-config-once')
    app.router.add_route('*', '/game-config', GameConfig, name='game-config')
    app.router.add_route(
        '*', '/asterios/{team}/member/{member}', AsteriosView, name='asterios')
