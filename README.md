missile-command
===============

Missile Command in 100 lines of Python using pygame

This started out as a challenge I posed to my friend David Do to write Missile
Command in 100 lines of Python. 

Challenge Rules:
* 4-space indents, one statement per line (no semicolons!)
* 79 characters per line maximum (as per PEP-8)

Notes:

* All game objects are of the same type, and that type copies keyword 
  arguments from the constructor into attributes. This seems like a good
  tradeoff between reducing line count and maintaining readability. 
* Lambdas are used instead of functions to reduce line count.
* Multi-warhead missiles will start appearing on later levels.

TODO:

* Add high score table (estimated cost: 8 lines)
