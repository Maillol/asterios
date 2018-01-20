Asterios
========

Launch server
-------------

PYTHONPATH=./sample/:$PYTHONPATH python -m asterios --level-package compute


Create a new game
-----------------

request
~~~~~~~

POST http://127.0.0.1:8000/game-config

    ``` json
    {"team": "team-17",
     "team_members": [
         {"name": "Toto"}
     ],
     "duration": 10}
    ```

response
~~~~~~~~

    ``` json
    {"duration": 10,
     "state": "ready",
     "team": "team-17",
     "team_members": [
        {"id": 1713,
         "level": 1,
         "level_max": 2,
         "name": "Toto"}]}
    ```

Start the created game
----------------------

request
~~~~~~~

PUT http://127.0.0.1:8000/game-config/team-17

response
~~~~~~~~

``` json
{
  "duration": 10,
  "team_members": [{
    "id": 1713,
    "level_max": 2,
    "name": "Toto",
    "level": 1
  }],
  "state": "start",
  "start_at": "2018-01-20T09:27:19.774612",
  "remaining": 10,
  "team": "team-17"
}
```

The team member Toto can get a puzzle sending GET request with his id 1713. 

GET http://127.0.0.1:8000/asterios/team-17/member/1713

{
  "tip": "II + II -> 4",
  "puzzle": "III + II"
}

The team member can send solved puzzle using POST request.

POST http://127.0.0.1:8000/asterios/team-17/member/1713

When the team member has solved all the puzzle, the field `win_at` is set


GET http://127.0.0.1:8000/game-config/team-17

``` json
{
  "duration": 10,
  "team_members": [{
    "win_at": "2018-01-20T09:35:33.706995",
    "id": 1713,
    "level_max": 2,
    "name": "Toto",
    "level": 2
  }],
  "state": "start",
  "start_at": "2018-01-20T09:27:19.774612",
  "remaining": 1,
  "team": "team-17"
}
```
