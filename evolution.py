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


# Player class
class Player(pygame.sprite.Sprite):
	def __init__(self, gs = None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("media/fish.png")
		self.rect = self.image.get_rect()

		self.velocity = 2
		
		# Keep original image to limit resize errors
		self.orig_image = self.image

		self.dx = 0
		self.dy = 0

	# Tick function, handles collision detection and eating once
	# we implement that
	def tick(self):
		# Get mouse x and y
		mx, my = pygame.mouse.get_pos()

		# Calculate the angle between current direction and mouse position
		px = self.rect.centerx
		py = self.rect.centery

		# Move the player based on keys pressed
		self.rect = self.rect.move(self.dx, self.dy)


	def move(self):
		# This uses the bit vector style of moving, simply because it's easier than
		# the more sophisticated implementation
		pressed = pygame.key.get_pressed()
		self.dx = 0
		self.dy = 0

		# Set the movement direction based on the keys pressed
		if pressed[pygame.K_RIGHT]:
			self.dx = self.velocity
		if pressed[pygame.K_LEFT]:
			self.dx = -1 * self.velocity
		if pressed[pygame.K_UP]:
			self.dy = -1 * self.velocity
		if pressed[pygame.K_DOWN]:
			self.dy = self.velocity


# Gamespace class for the main game
class GameSpace:
	def main(self):
		# Basic intialization
		pygame.init()
		pygame.key.set_repeat(25, 25)
		
		self.size = self.width, self.height = 640, 480
		self.black = 0, 0, 0

		# Object arrays
		self.lasers = []
		self.objects = []
		
		self.screen = pygame.display.set_mode(self.size)
		pygame.display.set_caption("Evolution - Eat or be eaten")

		# Set up sounds
		#pygame.mixer.init()
		#self.explodeSound = pygame.mixer.Sound("explode.wav")
		#self.laserSound = pygame.mixer.Sound("screammachine.wav")

		
		# Set up the game objects
		self.clock = pygame.time.Clock()
		self.player = Player(self)
		#self.earth = Earth(self)
		self.objects.append(self.player)
		#self.objects.append(self.earth)
		
		
		# Start the game loop
		quit = False
		while quit == False:
			# Set clock tick regulation
			self.clock.tick(60)
			
			# Handle input
			for event in pygame.event.get():
				if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
					quit = True
					break
				elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
					self.player.move()
				elif event.type == pygame.MOUSEBUTTONDOWN:
					#self.player.fire()
					pass
				elif event.type == pygame.MOUSEBUTTONUP:
					#self.player.stopFire()
					pass
			
			# Send a tick to every game object
			for l in self.lasers:
				l.tick()
			for o in self.objects:
				o.tick()
			
			# Display game objects
			self.screen.fill(self.black)
			for o in self.objects:
				self.screen.blit(o.image, o.rect)
			for l in self.lasers:
				self.screen.blit(l.image, l.rect)
			
			pygame.display.flip()

		# Quit the game
		pygame.quit()


if __name__ == "__main__":
	# Check the number of command line arguments
	args = sys.argv
	if len(args) != 2:
		print "Usage: python " + str(args[0]) + " <host|client>"
		sys.exit(1)

	# Setup pygame stuff, initialize the game
	gs = GameSpace()
	gs.main()