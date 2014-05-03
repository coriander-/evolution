# Evolution.py - Main game file
# Evolution is a multiplayer, networked game created as a final project
# for the Programming Paradigms class

# Authors: Nick Burns (nburns3@nd.edu, coriander-)
#		   Zach Lipp (zlipp@nd.edu)

# Current version: 0.10 (May 3, 2014)

# Usage: python evolution.py <options> (not sure what all the options will be yet)

# Game imports
import pygame
from pygame.locals import *

# Networking imports
from twisted.internet import reactor
from twisted.internet.protocol import Protocol, Factory, ReconnectingClientFactory
from twisted.internet.defer import DeferredQueue

# Misc imports
import sys
import math


if __name__ == "__main__":
	# Check the number of command line arguments
	args = sys.argv
	if len(args) != 2:
		print "Usage: python " + str(args[0]) + " <host|client>"
		sys.exit(1)