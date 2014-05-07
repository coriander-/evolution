# Evolution.py - Main game file
# Evolution is a multiplayer, networked game created as a final project
# for the Programming Paradigms class

# Authors: Nick Burns (nburns3@nd.edu, coriander-)
#		   Zach Lipp (zlipp@nd.edu)

# Current version: 0.80 (May 3, 2014)

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


# Class to store the game state in
class GameState:
	def __init__(self):

		self.fish_height = []
		self.fish_width = []
		self.fish_dx = []
		self.fish_x = []
		self.fish_y = []

		self.opponent_height = 0
		self.opponent_width = 0
		self.opponent_dx = 0
		self.opponent_dy = 0
		self.opponent_x = 0
		self.opponent_y = 0


# Class for miscellaneous fish
class Fish(pygame.sprite.Sprite):
	def __init__(self, gs = None, height = 1, width = 1, dx = 0, x = 0, y = 0):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("media/fish_red.png")
		self.rect = self.image.get_rect()

		# Keep original image to limit resize errors
		self.orig_image = self.image
		self.orig_flipped = pygame.transform.flip(self.orig_image, True, False)

		if self.gs.isPlayer1:
			# Determine whether the fish travels right or left
			self.right = random.randint(0, 1)
			self.rect.centery = random.randint(10, gs.height)

			# Randomize the size of the fish (width = 1.5 * height)
			self.height = random.randint(20, 150)
			self.width = int(self.height * 1.5)
			self.area = self.width * self.height
			self.velocity = (150 * 150 * 1.5) / self.area

			# Cap velocity at 7
			if self.velocity > 7:
				self.velocity = 7

			if self.right:
				self.dx = self.velocity
				self.rect.centerx = -100
				self.image = pygame.transform.scale(self.orig_image, (self.width, self.height))
				#self.rect = self.image.get_rect()
			else:
				self.dx = -1 * self.velocity
				self.rect.centerx = gs.width + 100
				#self.image = self.orig_flipped
				self.image = pygame.transform.scale(self.orig_flipped, (self.width, self.height))
				#self.rect = self.image.get_rect()

		else:
			# set everything if we're not the server
			self.height = height
			self.width = width
			self.dx = dx
			self.rect.centerx = x
			self.rect.centery = y

			self.area = self.width * self.height
			self.velocity = (150 * 150 * 1.5) / self.area

			if dx > 0:
				self.image = pygame.transform.scale(self.orig_image, (self.width, self.height))
			else:
				self.image = pygame.transform.scale(self.orig_flipped, (self.width, self.height))





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
	def __init__(self, gs = None, xstart = 50, ystart = 50):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("media/fish.png")
		self.rect = self.image.get_rect()

		#self.velocity = 9
		
		# Keep original image to limit resize errors
		self.orig_image = self.image
		self.orig_flipped = pygame.transform.flip(self.orig_image, True, False)

		self.width = 75
		self.height = 50

		self.right = pygame.transform.scale(self.orig_image, (self.width, self.height))
		self.left = pygame.transform.scale(self.orig_flipped, (self.width, self.height))

		self.area = self.width * self.height
		self.velocity = (150 * 150 * 1.5) / self.area

		self.image = self.right
		self.rect = self.image.get_rect()
		self.rect.centerx = xstart
		self.rect.centery = ystart

		self.dx = 0
		self.dy = 0

	# Tick function, handles collision detection and eating once
	# we implement that
	def tick(self):
		# Get mouse x and y
		mx, my = pygame.mouse.get_pos()

		print "Right edge of collision rectangle: " + str(self.rect.right)

		# Calculate the angle between current direction and mouse position
		px = self.rect.centerx
		py = self.rect.centery

		#set facing
		if self.dx<0:
			#self.image = self.orig_flipped
			self.image = self.left
		elif self.dx>0:
			#self.image = self.orig_image
			self.image = self.right
		# Move the player based on keys pressed
		self.rect = self.rect.move(self.dx, self.dy)

		# Check for collisions with the computer fish
		self.check_collisions()

	def check_collisions(self):
		# Check for collision with edge of window, kill velocity if it's at edge
		if self.rect.right >= self.gs.width or self.rect.left <= 0:
			self.dx = 0
		if self.rect.bottom >= self.gs.height or self.rect.top <= 0:
			self.dy = 0

		# Check for collision with a fish, eat it if it's smaller
		self.area = self.width * self.height
		collide = self.rect.collidelist(self.gs.fish)
		if collide != -1:
			fishWidth = self.gs.fish[collide].width
			fishHeight = self.gs.fish[collide].height
			fishArea = fishWidth * fishHeight

			#print "Collision data:"
			#print "Player area: " + str(self.area)
			#print "Fish area: " + str(fishArea)

			if fishArea < self.area:
				#print "Eating a fish!"

				# Remove fish
				del self.gs.fish[collide]

				# Add 1/10th of height and width of the eaten fish to player's size
				self.width += int(fishWidth / 10)
				self.height += int(fishHeight / 10)

				self.right = pygame.transform.scale(self.orig_image, (self.width, self.height))
				self.left = pygame.transform.scale(self.orig_flipped, (self.width, self.height))

				# Reset the current fish image
				if self.dx < 0:
					self.image = self.left
				else:
					self.image = self.right
				
				# Set the proper size
				self.rect.width = self.width
				self.rect.height = self.height
				self.area = self.width * self.height

		# Now check for collision with the other player, eat it and game over if bigger
		collidePlayer = self.rect.colliderect(self.gs.opponent.rect)
		if collidePlayer:
			#print "Collide is " + str(collide)
			#print "Number of objects is " + str(len(self.gs.objects))
			fishArea = self.gs.opponent.area
			if fishArea > self.area:
				print "Other player wins!"
				self.gs.reset()
			elif self.area > fishArea:
				print "You win!"
				self.gs.reset()



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
			self.image = self.right
		if pressed[pygame.K_LEFT] and self.rect.left >= 0:
			self.dx = -1 * self.velocity
			self.image = self.left
		if pressed[pygame.K_UP] and self.rect.top >= 0:
			self.dy = -1 * self.velocity
		if pressed[pygame.K_DOWN] and self.rect.bottom <= self.gs.height:
			self.dy = self.velocity

	def setSize(self, width, height):
		self.width = width
		self.height = height
		self.right = pygame.transform.scale(self.orig_image, (self.width, self.height))
		self.left = pygame.transform.scale(self.orig_flipped, (self.width, self.height))


# Class to generate fish at random intervals based on the length of the game
class FishGenerator:
	def __init__(self, gs = None):
		self.gs = gs
		self.ticks = 0
		self.maxfish = 2

	def tick(self):
		self.ticks += 1
		self.setMaxFish()
		# If not enough fish, 5% chance to generate a new fish
		if len(self.gs.fish) < self.maxfish and random.random() >= 0.95:
			self.gs.fish.append(Fish(self.gs))


	# Function to set the maximum number of fish on the screen 
	# based on the length of the game so far
	def setMaxFish(self):
		# 5 seconds
		if self.ticks == 5 * 60:
			self.maxfish = 4
		# 15 seconds
		elif self.ticks == 15 * 60:
			self.maxfish = 8
		# 30 seconds
		elif self.ticks == 30 * 60:
			self.maxfish = 15



# Gamespace class for the main game
class GameSpace:
	# Function to call each game loop (for networking integration)
	# Returns true if game should quit, false otherwise
	def loop_iteration(self):

		# Handle input

		for event in pygame.event.get():
			if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
				#print 'here'
				self.q.put('QUIT')
				return True
				#break
			elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
				self.player.move()
		
		# Send a tick to every game object
		if self.isPlayer1:
			for l in self.fish:
				l.tick()
		for o in self.objects:
			o.tick()

		# Generate new fish (as long as we're player 1)
		if self.isPlayer1:
			self.fish_generator.tick()
		
		#add to queue, send data
		self.q.put('1')

		# Display game objects
		self.screen.fill(self.black)
		self.screen.blit(self.backdrop, (0,0))
		for l in self.fish:
			self.screen.blit(l.image, l.rect)
		for i, o in enumerate(self.objects):
			#rect = o.image.get_rect()
			#print "Fish " + str(i) + " width: " + str(rect.width) + " rect width: " + str(o.rect.width)
			self.screen.blit(o.image, o.rect)
		
		pygame.display.flip()
		return False


	def __init__(self, q, server = True):
		# Basic intialization
		pygame.init()
		pygame.key.set_repeat(25, 25)

		self.isPlayer1 = server

		self.game_state = GameState()
		
		self.q = q
		self.size = self.width, self.height = 1000, 480
		self.black = 0, 0, 0
		self.backdrop = pygame.image.load("media/background.png")

		# Object arrays
		self.fish = []
		self.objects = []
		
		self.screen = pygame.display.set_mode(self.size)
		pygame.display.set_caption("Evolution - Eat or be eaten")

		# Set up the game objects
		self.clock = pygame.time.Clock()
		self.reset()

		# Set up sounds
		#pygame.mixer.init()
		#self.explodeSound = pygame.mixer.Sound("explode.wav")
		#self.laserSound = pygame.mixer.Sound("screammachine.wav")

	def main(self):	
		# Start the game loop
		quit = False
		while quit == False:
			# Set clock tick regulation
			self.clock.tick(60)

			quit = self.loop_iteration()
			

		# Quit the game
		pygame.quit()

	# Function to set up the gamespace
	def reset(self):
		# Empty the fish and object lists
		del self.fish[:]
		del self.objects[:]

		# Set up all game objects
		self.player1 = Player(self, 50, 50)
		self.player2 = Player(self, 900, 400)
		self.objects.append(self.player1)
		self.objects.append(self.player2)

		# Set the player based on the command line arg
		if self.isPlayer1:
			self.player = self.player1
			self.opponent = self.player2
		else:
			self.player = self.player2
			self.opponent = self.player1

		# Initialize the computer fish generator
		self.fish_generator = FishGenerator(self)

	def pack(self):
		# Clear all arrays in the game state
		del self.game_state.fish_height[:]
		del self.game_state.fish_width[:]
		del self.game_state.fish_dx[:]
		del self.game_state.fish_x[:]
		del self.game_state.fish_y[:]

		self.game_state.opponent_height = 0
		self.game_state.opponent_width = 0
		self.game_state.opponent_dx = 0
		self.game_state.opponent_dy = 0
		self.game_state.opponent_x = 0
		self.game_state.opponent_y = 0

		# Fish array
		for fish in self.fish:
			self.game_state.fish_height.append(fish.height)
			self.game_state.fish_width.append(fish.width)
			self.game_state.fish_dx.append(fish.dx)
			self.game_state.fish_x.append(fish.rect.centerx)
			self.game_state.fish_y.append(fish.rect.centery)

		# Objects
		self.game_state.opponent_height = self.player.height
		self.game_state.opponent_width = self.player.width
		self.game_state.opponent_dx = self.player.dx
		self.game_state.opponent_dy = self.player.dy
		self.game_state.opponent_x = self.player.rect.centerx
		self.game_state.opponent_y = self.player.rect.centery

	def unpack(self):
		# Delete all fish and re-initialize
		if not self.isPlayer1:
			del self.fish[:]
			for height in self.game_state.fish_height:
				newFish = Fish(self, height, self.game_state.fish_width.pop(0), self.game_state.fish_dx.pop(0), self.game_state.fish_x.pop(0), self.game_state.fish_y.pop(0))
				#newFish.height = height
				#newFish.width = self.game_state.fish_width.pop(0)
				#newFish.dx = self.game_state.fish_dx.pop(0)
				#newFish.rect.centerx = self.game_state.fish_x.pop(0)
				#newFish.rect.centery = self.game_state.fish_y.pop(0)
				self.fish.append(newFish)

		self.opponent.height = self.game_state.opponent_height
		self.opponent.width = self.game_state.opponent_width
		self.opponent.dx = self.game_state.opponent_dx
		self.opponent.dy = self.game_state.opponent_dy
		self.opponent.rect.centerx = self.game_state.opponent_x
		self.opponent.rect.centery = self.game_state.opponent_y


		# for player in self.objects:
		# 	if self.game_state.player_height:
		# 		player.height = self.game_state.player_height.pop(0)
		# 		player.width = self.game_state.player_width.pop(0)
		# 		player.dx = self.game_state.player_dx.pop(0)
		# 		player.dy = self.game_state.player_dy.pop(0)
		# 		player.x = self.game_state.player_x.pop(0)
		# 		player.y = self.game_state.player_y.pop(0)


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
