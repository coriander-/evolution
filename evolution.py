# Evolution.py - Main game file
# Evolution is a multiplayer, networked game created as a final project
# for the Programming Paradigms class

# Authors: Nick Burns (nburns3@nd.edu, coriander-)
#		   Zach Lipp (zlipp@nd.edu)

# Current version: 0.50 (May 3, 2014)

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
import random


# Class for miscellaneous fish
class Fish(pygame.sprite.Sprite):
	def __init__(self, gs = None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("media/fish_red.png")
		self.rect = self.image.get_rect()

		self.velocity = random.randint(1, 5)

		# Determine whether the fish travels right or left
		self.right = random.randint(0, 1)
		self.rect.centery = random.randint(10, gs.height)

		# Keep original image to limit resize errors
		self.orig_image = self.image
		self.orig_flipped = pygame.transform.flip(self.orig_image, True, False)

		if self.right:
			self.dx = self.velocity
			self.rect.centerx = -100
		else:
			self.dx = -1 * self.velocity
			self.rect.centerx = gs.width + 100
			self.image = self.orig_flipped
			#self.image = pygame.transform.scale(self.orig_flipped, (100, 50))

	def tick(self):
		# Move the fish
		# Move the player based on keys pressed
		self.rect = self.rect.move(self.dx, 0)

		# Determine if fish has traveled too far off screen and should be destroyed
		if self.right:
			if self.rect.left > self.gs.width:
				self.gs.fish.remove(self)
		else:
			if self.rect.right < 0:
				self.gs.fish.remove(self)


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
		self.orig_flipped = pygame.transform.flip(self.orig_image, True, False)

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

		# Set the movement direction based on the keys pressed (also make
		# the fish go the other direction)
		if pressed[pygame.K_RIGHT] and self.rect.right <= self.gs.width:
			self.dx = self.velocity
			self.image = self.orig_image
		if pressed[pygame.K_LEFT] and self.rect.left >= 0:
			self.dx = -1 * self.velocity
			self.image = self.orig_flipped
		if pressed[pygame.K_UP] and self.rect.top >= 0:
			self.dy = -1 * self.velocity
		if pressed[pygame.K_DOWN] and self.rect.bottom <= self.gs.height:
			self.dy = self.velocity


# Gamespace class for the main game
class GameSpace:
	# Function to call each game loop (for networking integration)
	# Returns true if game should quit, false otherwise
	def loop_iteration(self):
		# Handle input

		for event in pygame.event.get():
			if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
				return True
				#break
			elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
				self.player.move()
			elif event.type == pygame.MOUSEBUTTONDOWN:
				#self.player.fire()
				self.fish.append(Fish(self))
				pass
			elif event.type == pygame.MOUSEBUTTONUP:
				#self.player.stopFire()
				pass
		
		# Send a tick to every game object
		for l in self.fish:
			l.tick()
		for o in self.objects:
			o.tick()
		
		# Display game objects
		self.screen.fill(self.black)
		self.screen.blit(self.backdrop, (0,0))
		for l in self.fish:
			self.screen.blit(l.image, l.rect)
		for o in self.objects:
			self.screen.blit(o.image, o.rect)
		
		pygame.display.flip()

		return False


	def main(self):
		# Basic intialization
		pygame.init()
		pygame.key.set_repeat(25, 25)
		
		self.size = self.width, self.height = 1000, 480
		self.black = 0, 0, 0
		self.backdrop = pygame.image.load("media/background.png")

		# Object arrays
		self.fish = []
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

			quit = self.loop_iteration()
			

		# Quit the game
		pygame.quit()


if __name__ == "__main__":
	# Check the number of command line arguments
	args = sys.argv
	if len(args) != 2:
		print "Usage: python " + str(args[0]) + " <host|client>"
		sys.exit(1)

	# Seed the random number generator
	random.seed()

	# Setup pygame stuff, initialize the game
	gs = GameSpace()
	gs.main()