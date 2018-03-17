API
===

game configuration resource
---------------------------

Create a new game configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: asterios.views.GameConfig.post

Start a created game configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: asterios.views.GameConfig.put

Select the created games configurations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: asterios.views.GameConfig.get

Delete an existing game configurations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: asterios.views.GameConfig.delete


Play with started game configuration
------------------------------------

Get the current puzzle
^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: asterios.views.AsteriosView.get


Send the solved puzzle
^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: asterios.views.AsteriosView.post


