import pygame
import random
from random import randrange
from random import choice
from Setting import *


# Initializing SpriteSheet Class
class SpriteSheet:
	# Utility Class For Loading And Parsing SpriteSheet
	def __init__(self, filename):
		self.spritesheet = pygame.image.load(filename).convert()

	def get_image(self, x, y, width, height):
		# Grab An Image Out Of A Larger SpriteSheet 
		image = pygame.Surface((width, height))
		image.blit(self.spritesheet, (0, 0), (x, y, width, height))
		image = pygame.transform.scale(image, (width // 2, height // 2))
		return image


# Initializing The Player Sprite
class Player(pygame.sprite.Sprite):
	def __init__(self, game):
		self._layer = PLAYER_LAYER
		self.groups = game.all_sprites
		pygame.sprite.Sprite.__init__(self, self.groups)
		self.game = game
		self.walking = False
		self.jumping = False
		self.current_frame = 0
		self.last_update = 0
		self.load_images()
		self.image = self.standing_frames[0]
		self.rect = self.image.get_rect()
		self.rect.center = (WIDTH / 2, HEIGHT / 2)
		self.pos = vec(40, HEIGHT - 100)
		self.vel = vec(0, 0)
		self.acc = vec(0, 0)

	def load_images(self):
		self.standing_frames = [self.game.spritesheet.get_image(614, 1063, 120, 191), 
								self.game.spritesheet.get_image(690, 406, 120, 201)]
		for frame in self.standing_frames:
			frame.set_colorkey(BLACK)

		self.walk_frames_right = [self.game.spritesheet.get_image(678, 860, 120, 201),
								  self.game.spritesheet.get_image(692, 1458, 120, 207)]
			
		self.walk_frames_left = []
		for frame in self.walk_frames_right:
			frame.set_colorkey(BLACK)
			self.walk_frames_left.append(pygame.transform.flip(frame, True, False))

		self.jump_frame = self.game.spritesheet.get_image(416, 1660, 150, 181)
		self.jump_frame.set_colorkey(BLACK)

	def jump_cut(self):
		if self.jumping:
			if self.vel.y < -3:
				self.vel.y = -3

	def jump(self):
		# Only Able To Jump If There Is Something Underneath
		self.rect.x += 2
		hits = pygame.sprite.spritecollide(self, self.game.platforms, False)
		self.rect.x -= 2
		if hits and not self.jumping:
			self.game.jump_sound.play()
			self.jumping = True
			self.vel.y = -PLAYER_JUMP

	def update(self):
		self.animate()
		self.acc = vec(0, PLAYER_GRAV)
		keys = pygame.key.get_pressed()
		if keys[pygame.K_LEFT]:
			self.acc.x = -PLAYER_ACC
		if keys[pygame.K_RIGHT]:
			self.acc.x = PLAYER_ACC

		# Applying Friction
		self.acc.x += self.vel.x * PLAYER_FRICTION

		# Using Equations Of Motion
		self.vel += self.acc
		if abs(self.vel.x) < 0.1:
			self.vel.x = 0
		self.pos += self.vel + 0.5 * self.acc

		# Wrap Around The Sides Of The Screen
		if self.pos.x > WIDTH + self.rect.width / 2:
			self.pos.x = 0 - self.rect.width / 2
		if self.pos.x < 0 -  self.rect.width / 2:
			self.pos.x = WIDTH +  self.rect.width / 2

		self.rect.midbottom = self.pos

	def animate(self):
		now = pygame.time.get_ticks()

		# Cheacking If We Are Walking
		if self.vel.x != 0:
			self.walking = True
		else:
			self.walking = False

		## Walking Animation
		if self.walking:
			if now - self.last_update > 170:
				self.last_update = now
				self.current_frame = (self.current_frame + 1) % len(self.walk_frames_right)
				bottom = self.rect.bottom
				if self.vel.x > 0:
					self.image = self.walk_frames_right[self.current_frame]
				else:
					self.image = self.walk_frames_left[self.current_frame]
				self.rect = self.image.get_rect()
				self.rect.bottom = bottom

		# Idle Animation
		if not self.jumping and not self.walking:
			if now - self.last_update > 350:
				self.last_update = now
				self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
				bottom = self.rect.bottom
				self.image = self.standing_frames[self.current_frame]
				self.rect = self.image.get_rect()
				self.rect.bottom = bottom

		# Pixel Perfect Collision
		self.mask = pygame.mask.from_surface(self.image)

class Cloud(pygame.sprite.Sprite):
	def __init__(self, game):
		self._layer = CLOUD_LAYER
		self.groups = game.all_sprites, game.clouds
		pygame.sprite.Sprite.__init__(self, self.groups)
		self.game = game
		self.image = choice(self.game.cloud_images)
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		scale = randrange(50 ,101) / 100
		self.image = pygame.transform.scale(self.image, (int(self.rect.width * scale), int(self.rect.height * scale)))
		self.rect.x = randrange(WIDTH - self.rect.width)
		self.rect.y = randrange(-500, -50)

	def Update():
		if self.rect.top > HEIGHT * 2:
			self.kill()

class Platform(pygame.sprite.Sprite):
	def __init__(self, game, x, y):
		self._layer = PLATFORM_LAYER
		self.groups = game.all_sprites, game.platforms
		pygame.sprite.Sprite.__init__(self, self.groups)
		self.game = game
		images = [self.game.spritesheet.get_image(0, 288, 380, 94),
		          self.game.spritesheet.get_image(213, 1662, 201, 100)]
		self.image = random.choice(images)
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		if randrange(100) < POW_SPAWM_FREQUENCY:
			PowerUp(self.game, self)

class PowerUp(pygame.sprite.Sprite):
	def __init__(self, game, plat):
		self._layer = POWER_LAYER
		self.groups = game.all_sprites, game.powerups
		pygame.sprite.Sprite.__init__(self, self.groups)
		self.game = game
		self.plat = plat
		self.type = choice(["boost"])
		self.image = self.game.spritesheet.get_image(820, 1805, 71, 70)
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		self.rect.centerx = self.plat.rect.centerx
		self.rect.bottom = self.plat.rect.top - 5

	def update(self):
		# Moves The PowerUp When The Platform Moves
		self.rect.bottom = self.plat.rect.top - 5

		# Removes Powerup When Platform Is Removed
		if not self.game.platforms.has(self.plat):
			self.kill()

class Mob(pygame.sprite.Sprite):
	def __init__(self, game):
		self._layer = MOB_LAYER
		self.groups = game.all_sprites, game.mobs
		pygame.sprite.Sprite.__init__(self, self.groups)
		self.game = game
		self.image_up = self.game.spritesheet.get_image(566, 510, 122, 139)
		self.image_up.set_colorkey(BLACK)
		self.image_down = self.game.spritesheet.get_image(568, 1534, 122, 135)
		self.image_down.set_colorkey(BLACK)
		self.image = self.image_up
		self.rect = self.image.get_rect()
		self.rect.centerx = choice([-100, WIDTH + 100])
		self.velx = randrange(1, 4)
		if self.rect.centerx > WIDTH:
			self.velx *= -1
		self.rect.y = randrange(HEIGHT / 2)
		self.vely = 0
		self. altvel = 0.5

	def update(self):
		self.rect.x += self.velx
		self.vely += self.altvel
		if self.vely > 3 or self.vely < -3:
			self.altvel *= -1
		center = self.rect.center
		if self.altvel < 0:
			self.image = self.image_up
		else:
			self.image = self.image_down
		self.rect = self.image.get_rect()
		self.mask = pygame.mask.from_surface(self.image)
		self.rect.center = center
		self.rect.y += self.vely
		if self.rect.left > WIDTH + 100 or self.rect.right < -100:
			self.kill()


