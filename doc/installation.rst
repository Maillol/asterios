Installation
============

pip install asterios

Running
=======




http://127.0.0.1:8080/oas/spec


python -m asterios_client set_conf
    --host http://127.0.0.1:8080
    --team team-17
    --member-id 2013

python -m asterios_client generate_module




$ python -m asterios_client show --tip

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

$ python -m asterios_client show --puzzle
['    ↓ \n┌─── ┐\n├ ───┤\n├─── ┤\n└─ ──┘\n      ',
 ' ↓    \n┌ ───┐\n├── ─┤\n├─── ┤\n└─ ──┘\n      ',
 '   ↓  \n┌── ─┐\n├─── ┤\n├─── ┤\n└─── ┘\n      ',
 '  ↓   \n┌─ ──┐\n├─ ──┤\n├ ───┤\n└── ─┘\n      ',
 '   ↓  \n┌── ─┐\n├─── ┤\n├── ─┤\n└─── ┘\n      ',
 '  ↓   \n┌─ ──┐\n├─ ──┤\n├── ─┤\n└ ───┘\n      ',
 '   ↓  \n┌── ─┐\n├ ───┤\n├─── ┤\n└─ ──┘\n      ']


Open "asterios_solver.py" file and edit the solve function to solve the function.




python asterios_solver.py