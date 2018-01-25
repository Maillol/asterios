# PYTHONPATH=$PWD/tests/data_test_functional/:$PYTHONPATH python3 -m
# unittest -v tests.test_functional
from datetime import datetime
import os

from cricri import Condition, TestServer, condition, previous


class Count(Condition):

    def __init__(self, step, count):
        self.step = step
        self.count = count

    def __call__(self, previous_steps):
        previous_steps = tuple(previous_steps)
        return previous_steps.count(self.step) == self.count


class TestRestServer(TestServer):

    commands = [
        {
            "name": "asterios",
            "cmd": ["python3", "-u", "-m", "asterios",
                    "--port", "{port-1}",
                    "--level-package", "levels_theme_1",
                    "--level-package", "levels_theme_2"],
            "extra-env": {
                'PYTHONPATH': 'tests/data_test_functional'
            }
        }
    ]

    http_clients = [
        {
            "name": "G. Hammond",
            "host": "127.0.0.1",
            "port": "{port-1}",
            "extra_headers": [
                ('Content-Type', 'application/json')
            ]
        },
        {
            "name": "D. Jackson",
            "host": "127.0.0.1",
            "port": "{port-1}",
            "extra_headers": [
                ('Content-Type', 'application/json')
            ]
        },
        {
            "name": "S. Carter",
            "host": "127.0.0.1",
            "port": "{port-1}",
            "extra_headers": [
                ('Content-Type', 'application/json')
            ]
        }
    ]

    data = {}


class Start(TestRestServer, start=True):
    def input(self):
        pass

    def test_server_listen(self):
        self.servers['asterios'].assert_stdout_regex(
            r'======== Running on http://127.0.0.1:\d+ ========', timeout=2
        )


class ConfigureANewGame(TestRestServer, previous=['Start']):

    def input(self):
        self.clients["G. Hammond"].post("/game-config",
                                        data={
                                            "team": "SG-1",
                                            "team_members": [
                                                {"name": "D. Jackson"},
                                                {"name": "S. Carter"}
                                            ],
                                            "duration": 10
                                        }
                                        )

    def test_status_code_should_be_201(self):
        self.clients["G. Hammond"].response.assert_status_code(201)

    def test_content_has_team_set_to_sg1(self):
        content = self.clients["G. Hammond"].response.content
        self.assertEqual(content['team'], 'SG-1')

    def test_content_has_state_set_to_ready(self):
        content = self.clients["G. Hammond"].response.content
        self.assertEqual(content['state'], 'ready')

    def test_team_member_jackson_has_an_id(self):
        content = self.clients["G. Hammond"].response.content
        self.assertIn('id', content['team_members'][0])
        self.data['jackson id'] = content['team_members'][0]['id']

    def test_team_member_jackson_has_a_theme(self):
        content = self.clients["G. Hammond"].response.content
        self.assertIn('levels_obj', content['team_members'][0])
        self.assertIn('theme', content['team_members'][0]['levels_obj'])
        self.data['jackson theme'] = content['team_members'][0]['levels_obj']['theme']

    def test_team_member_carter_has_an_id(self):
        content = self.clients["G. Hammond"].response.content
        self.assertIn('id', content['team_members'][1])
        self.data['carter id'] = content['team_members'][1]['id']

    def test_team_member_carter_has_a_theme(self):
        content = self.clients["G. Hammond"].response.content
        self.assertIn('levels_obj', content['team_members'][0])
        self.assertIn('theme', content['team_members'][0]['levels_obj'])
        self.data['carter theme'] = content['team_members'][0]['levels_obj']['theme']


class StartANewGame(TestRestServer, previous=['ConfigureANewGame',
                                              'StartANewGame']):

    def input(self):
        self.data['before'] = datetime.utcnow().isoformat()
        self.clients["G. Hammond"].put("/game-config/SG-1")
        self.data['after'] = datetime.utcnow().isoformat()

    @previous('ConfigureANewGame')
    def test_status_code_should_be_200(self):
        self.clients["G. Hammond"].response.assert_status_code(200)

    @previous('ConfigureANewGame')
    def test_game_has_remaining_field_set_to_duration(self):
        content = self.clients["G. Hammond"].response.content
        self.assertTrue(0 <= content['remaining'] <= content['duration'])

    @previous('ConfigureANewGame')
    def test_game_has_start_field_set(self):
        content = self.clients["G. Hammond"].response.content
        self.assertTrue(
            self.data['before'] <= content['start_at'] <= self.data['after'])

    @previous('StartANewGame')
    def test_status_code_should_be_409(self):
        self.clients["G. Hammond"].response.assert_status_code(409)

    @previous('StartANewGame')
    def test_content_should_be_game_already_started(self):
        content = self.clients["G. Hammond"].response.content
        self.assertEqual(content,
                         {'message': 'The game `SG-1` is already started'})


class DanielJacksonSendWrongResponse(
    TestRestServer,
    previous=['StartANewGame',
              'DanielJacksonSendWrongResponse',
              'DanielJacksonSendRightResponse']):

    def input(self):
        url = "/asterios/SG-1/member/{}".format(self.data['jackson id'])
        self.clients["D. Jackson"].post(url, data="wrong response")

    @condition(Count('DanielJacksonSendRightResponse', 0) |
               Count('DanielJacksonSendRightResponse', 1))
    def test_status_code_should_be_420(self):
        self.clients["D. Jackson"].response.assert_status_code(420)

    @condition(Count('DanielJacksonSendRightResponse', 2))
    def test_status_code_should_be_409(self):
        content = self.clients["D. Jackson"].response.content
        self.assertEqual(content, {'message': 'You win!'})

    @condition(Count('DanielJacksonSendRightResponse', 0) |
               Count('DanielJacksonSendRightResponse', 1))
    def test_content_should_be_wrong_response(self):
        content = self.clients["D. Jackson"].response.content
        self.assertEqual(content, "wrong response")

    @condition(Count('DanielJacksonSendRightResponse', 2))
    def test_content_should_be_you_win(self):
        content = self.clients["D. Jackson"].response.content
        self.assertEqual(content, {'message': 'You win!'})


class DanielJacksonSendRightResponse(
    TestRestServer,
    previous=['StartANewGame',
              'DanielJacksonSendWrongResponse',
              'DanielJacksonSendRightResponse']):

    def input(self):
        url = "/asterios/SG-1/member/{}".format(self.data['jackson id'])
        self.clients["D. Jackson"].post(url, data="right answer")

    @condition(Count('DanielJacksonSendRightResponse', 0))
    def test_content_should_be_go_to_level_2(self):
        content = self.clients["D. Jackson"].response.content

    @condition(Count('DanielJacksonSendRightResponse', 1))
    def test_content_should_be_finish(self):
        content = self.clients["D. Jackson"].response.content
        self.assertEqual(content, 'Finish {}'.format(
            self.data['jackson theme']))


class SamanthaCarterSendRightResponse(
        TestRestServer,
        previous=['ConfigureANewGame']):

    def input(self):
        url = "/asterios/SG-1/member/{}".format(self.data['jackson id'])
        self.clients["S. Carter"].post(url, data="right answer")

    def test_status_code_should_be_409(self):
        self.clients["S. Carter"].response.assert_status_code(409)

    def test_content_should_be_game_is_not_started(self):
        content = self.clients["S. Carter"].response.content
        self.assertEqual(
            content, {'message': 'The game `SG-1` is not started'})


load_tests = TestRestServer.get_load_tests()
