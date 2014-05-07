Evolution
=========

Readme for the final project for Programming Paradigms, Spring 2014.  A multiplayer networked game using the Pygame and Twisted libraries.

This game is a twist on the classic "eat smaller fish to grow" theme: you must compete with an opponent who might be bigger than you!

Setup
=====
Evolution.py contains the game code and network.py contains all the necessary networking for the game. To set up the game the server needs to launched first. It is launched with the command "python network.py server <port>". <port> is the port the server will listen on. Then the client can be run on a different machine with the command "python network client <hostname> <port>". <hostname> is the name of the host the server is running on and <port> the the port the server is listening on. 

Game Play
========
When a connection is made both client and server will jump into the game.

     Objective
     ========
     Eat the other player

     Rules
     ====
     To eat the other player you must be bigger than they are and then collide with them.
     To get bigger you must eat other fish (red) that are smaller than you.
     To eat smaller red fish all you have to do is catch them.

     Controls
     ========
     Arrow Keys - Move your fish

When a player wins the winner is displayed on the command line and the game restarts.
      