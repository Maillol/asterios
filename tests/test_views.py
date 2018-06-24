from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web
from asterios.views import GameConfig
from asterios.routes import setup_routes
import asterios.models
from asterios.models import GAMES, error_middleware
from asterios.level import MetaLevel, BaseLevel
import asyncio
from unittest import mock
from datetime import datetime


def _load_level():
    MetaLevel.clean()

    class Level1(BaseLevel):
        "resolve calcul"

        def __init__(self, difficulty):
            super().__init__(difficulty)
            self.puzzles = [
                ("2 + 2", 4),
                ("1 + 1", 2)
            ]

        def generate_puzzle(self):
            puzzle, self.expected = self.puzzles.pop()
            return puzzle

        def check_answer(self, answer):
            is_exact = answer == self.expected
            return (is_exact, ':-)' if is_exact else ':-|')

    class Level2(BaseLevel):
        "resolve calcul again"

        def generate_puzzle(self):
            return '2 * 3'

        def check_answer(self, answer):
            is_exact = 6 == self.expected
            return (is_exact, ':-)' if is_exact else ':-|')


class TestGameConfigView(AioHTTPTestCase):

    async def get_application(self):
        """
        Override the get_app method to return your application.
        """
        app = web.Application(middlewares=[error_middleware])
        setup_routes(app)
        return app

    def setUp(self):
        GAMES.drop()
        _load_level()
        super().setUp()

    @unittest_run_loop
    async def test_get_all(self):
        url = self.app.router['game-config'].url_for()
        request = await self.client.request("GET", url)
        self.assertEqual(request.status, 200)
        self.assertEqual((await request.json()), [])

    @unittest_run_loop
    async def test_get_unexisting(self):
        url = self.app.router['game-config-once'].url_for(name='unexisting')
        request = await self.client.request("GET", url)
        self.assertEqual(request.status, 404)
        self.assertEqual((await request.json()),
                         {'message': "The game with name `unexisting` doesn't exist",
                          'exception': 'GameDoesntExist'})

    @unittest_run_loop
    async def test_create_and_launch(self):

        with mock.patch('asterios.models.utcnow') as utcnow_mock:
            utcnow_mock.return_value = datetime(2018, 1, 1, 12, 0)

            with self.subTest(should='Create a game'):
                url = self.app.router['game-config'].url_for()
                request = await self.client.request(
                    "POST", url, json={
                        'team': 'team-17',
                        'team_members': [
                            {'theme': 'test_views',
                             'level': 1,
                             'name': 'Toto',
                             'level_max': 3},
                        ],
                        'state': 'ready',
                        'duration': 2
                    })
                game = await request.json()
                self.assertEqual(request.status, 201, game)
                self.assertNotIn('start_at', game)

            url = self.app.router['game-config-once'].url_for(name='team-17')
            with self.subTest(should='Start the created game'):
                request = await self.client.request(
                    "PUT", url, json={
                        'team': 'team-17',
                        'team_members': [
                            {'theme': 'test_views',
                             'level': 1,
                             'name': 'Toto',
                             'level_max': 3},
                        ],
                        'state': 'start',
                        'duration': 2
                    })

                game = await request.json()
                self.assertEqual(request.status, 200, game)
                self.assertEqual(game['start_at'], '2018-01-01T12:00:00')
                self.assertEqual(game['state'], 'start')
                self.assertEqual(game['remaining'], 2)

            with self.subTest(should='Remaining time should be 1'):
                utcnow_mock.return_value = datetime(2018, 1, 1, 12, 1)

                request = await self.client.request('GET', url)

                game = await request.json()
                self.assertEqual(request.status, 200, game)
                self.assertEqual(game['start_at'], '2018-01-01T12:00:00')
                self.assertEqual(game['state'], 'start')
                self.assertEqual(game['remaining'], 1)

            with self.subTest(should='Remaining time should be 0'):
                utcnow_mock.return_value = datetime(2018, 1, 1, 12, 2)

                request = await self.client.request('GET', url)

                game = await request.json()
                self.assertEqual(request.status, 200, game)
                self.assertEqual(game['start_at'], '2018-01-01T12:00:00')
                self.assertEqual(game['state'], 'stop')
                self.assertEqual(game['remaining'], 0)


class TestAsteriosView(AioHTTPTestCase):

    async def get_application(self):
        """
        Override the get_app method to return your application.
        """
        app = web.Application(middlewares=[error_middleware])
        setup_routes(app)
        return app

    def setUp(self):
        _load_level()
        GAMES.drop()
        GAMES.create({
            'team': 'SG1',
            'team_members': [
                {'level': 1,
                 'name': 'D. Jackson',
                 'level_max': 3},
                {'theme': 'tests.test_views',
                 'level': 1,
                 'name': 'S. Karter',
                 'level_max': 3},
            ],
            'duration': 60
        })

        with mock.patch('asterios.models.utcnow') as utcnow_mock:
            utcnow_mock.return_value = datetime(2018, 1, 1, 12, 0)
            GAMES.start('SG1')

            self.id_jackson = str(GAMES.member_from_name(
                'SG1', 'D. Jackson')['id'])
            self.id_karter = str(GAMES.member_from_name(
                'SG1', 'S. Karter')['id'])

        super().setUp()

    @unittest_run_loop
    async def test_1(self):
        url_jackson = self.app.router['asterios'].url_for(
            team='SG1', member=self.id_jackson)
        url_karter = self.app.router['asterios'].url_for(
            team='SG1', member=self.id_karter)

        with mock.patch('asterios.models.utcnow') as utcnow_mock:
            utcnow_mock.return_value = datetime(2016, 1, 1, 12, 0)
            with self.subTest(should='Get question should return 200'):
                request = await self.client.request('GET', url_jackson)
                json = await request.json()
                self.assertEqual(request.status, 200, json)
                self.assertEqual(json,
                                 {"tip": "resolve calcul",
                                  "puzzle": "1 + 1"})

            with self.subTest(should='Question should be change after each get'):
                request = await self.client.request('GET', url_jackson)
                json = await request.json()
                self.assertEqual(request.status, 200, json)
                self.assertEqual(json,
                                 {"tip": "resolve calcul",
                                  "puzzle": "2 + 2"})

            with self.subTest(should='return 420 if answer is wrong'):
                request = await self.client.request('POST', url_jackson, json=3412)
                json = await request.json()
                self.assertEqual(request.status, 420, json)
                self.assertEqual(json, ':-|')

            with self.subTest(should='return 201 if answer is right'):
                request = await self.client.request('POST', url_jackson, json=4)
                json = await request.json()
                self.assertEqual(request.status, 201, json)
                self.assertEqual(json, ':-)')

            with self.subTest(should='get question level 2 because previous is done'):
                request = await self.client.request('GET', url_jackson)
                json = await request.json()

                self.assertEqual(request.status, 200, json)
                self.assertEqual(json, {'tip': 'resolve calcul again',
                                        'puzzle': '2 * 3'})
