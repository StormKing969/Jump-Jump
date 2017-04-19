import pygame
import random
from Setting import *
from Sprites import *
from os import path

class Game:
	# Initialize Pygame & Create Window
	def __init__(self):
		pygame.init()
		pygame.mixer.init()  
		self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
		pygame.display.set_caption(TITLE)
		self.clock = pygame.time.Clock()
		self.running = True
		self.font_name = pygame.font.match_font(FONT_NAME)
 		self.load_data()

	# Starting Data
	def load_data(self):
		self.dir = path.dirname(__file__)

		if path.isfile(path.join(self.dir, HS_FILE)):
			self.file_exist = 'r+'
		else:
			self.file_exist = 'w'
		with open(path.join(self.dir, HS_FILE), self.file_exist) as data:
			try:
				self.highscore = int(data.read())
			except:
				self.highscore = 0

		# Load SpriteSheet Image
		img_dir = path.join(self.dir, 'Image')
		self.spritesheet = SpriteSheet(path.join(img_dir, SPRITESHEET))

		# Cloud Image
		self.cloud_images = []
		for i in range(1, 4):
			self.cloud_images.append(pygame.image.load(path.join(img_dir, "cloud{}.png".format(i))).convert())

		# Load Sound
		self.snd_dir = path.join(self.dir, "Sound")
		self.jump_sound = pygame.mixer.Sound(path.join(self.snd_dir, "Jump.wav"))
		self.boost_sound = pygame.mixer.Sound(path.join(self.snd_dir, "Boost.wav"))

	# Restarts The Game
	def new(self):
		self.score = 0
		self.all_sprites = pygame.sprite.LayeredUpdates()
		self.platforms = pygame.sprite.Group()
		self.powerups = pygame.sprite.Group()
		self.mobs = pygame.sprite.Group()
		self.clouds = pygame.sprite.Group()
		self.player = Player(self)
		for plat in PLATFORM_LIST:
			Platform(self, *plat)    # Same As (plat[0], y, w, h)
		self.mob_timer = 0
		pygame.mixer.music.load(path.join(self.snd_dir, "HappyTune.ogg"))
		for i in range(8):
			c = Cloud(self)
			c.rect.y += 500
		self.run()

	# Game Loop
	def run(self):		
		pygame.mixer.music.play(loops = -1)
		self.playing = True
		while self.playing:
			# Keep Loop Running At The Right Speed
			self.clock.tick(FPS)
			self.events()
			self.update()
			self.draw()
		pygame.mixer.music.fadeout(500)

	# Game Loop - Update
	def update(self):
		self.all_sprites.update()

		# Whether To Spawn A Mob
		now = pygame.time.get_ticks()
		if now - self.mob_timer > 5000 + random.choice([-1000, -500, 0, 500, 1000]):
			self.mob_timer = now
			Mob(self)

		# Player & Mob Collision
		mob_hits = pygame.sprite.spritecollide(self.player, self.mobs, False, pygame.sprite.collide_mask)
		if mob_hits:
			self.playing = False

		# Player & Platform Collision - Only If Falling
		if self.player.vel.y > 0:
			hits = pygame.sprite.spritecollide(self.player, self.platforms, False)
			if hits:
				lowest = hits[0]
				for hit in hits:
					if hit.rect.bottom > lowest.rect.bottom:
						lowest = hit

				# Edges
				if self.player.pos.x < lowest.rect.right + 5 and self.player.pos.x > lowest.rect.left - 5:
					if self.player.pos.y < lowest.rect.centery:
						self.player.pos.y = lowest.rect.top
						self.player.vel.y = 0
						self.player.jumping = False

		# If Player Reaches Top 1/4 Of Screen
		if self.player.rect.top <= HEIGHT * 1 / 3:
			if random.randrange(100) < 15:
				Cloud(self)
			self.player.pos.y += max(abs(self.player.vel.y), 2)
			for cloud in self.clouds:
				cloud.rect.y += max(abs(self.player.vel.y / (random.randrange(1, 3))), 2)
			for mob in self.mobs:
				mob.rect.y += max(abs(self.player.vel.y), 2)
			for plat in self.platforms:
				plat.rect.y += max(abs(self.player.vel.y), 2)
				if plat.rect.top >= HEIGHT:
					plat.kill()
					self.score += 1

		# Collision Between Player & PowerUp
		pow_hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
		for pow in pow_hits:
			if pow.type == "boost":
				self.boost_sound.play()
				self.player.vel.y = -BOOST_POWER
				self.player.jumping = False

		# If We Fall 
		if self.player.rect.bottom > HEIGHT:
			for sprite in self.all_sprites:
				sprite.rect.y -= max(self.player.vel.y, 5)
				if sprite.rect.bottom < 0:
					sprite.kill()
		if len(self.platforms) == 0:
			self.playing = False

		# Spawning New Platforms
		while len(self.platforms) < 6:
			width = random.randrange(50, 100)
			Platform(self, random.randrange(0, WIDTH - width), random.randrange(-75, -30))

	# Game Loop - Event
	def events(self):
		for event in pygame.event.get():
			# Checks For Closing Window
			if event.type == pygame.QUIT:
				if self.playing:
					self.playing = False
				self.running = False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					self.player.jump()
			if event.type == pygame.KEYUP:
				if event.key == pygame.K_SPACE:
					self.player.jump_cut()

	# Game Loop - Draw
	def draw(self):
		self.screen.fill(LIGHTBLUE)
		self.all_sprites.draw(self.screen)

		# Score
		self.draw_text(str(self.score), 22, WHITE, WIDTH/2, 15)
		
		# Alway Do The Flip Last (after drawing everything)
		pygame.display.flip()

	# Game Splash/Start Screen
	def show_start_screen(self):
		pygame.mixer.music.load(path.join(self.snd_dir, "Yippee.ogg"))
		pygame.mixer.music.play(loops = -1)
		self.screen.fill(LIGHTBLUE)
		self.draw_text(TITLE, 48, WHITE, WIDTH / 2, HEIGHT / 4)
		self.draw_text("Arrows To Move & Space To Jump", 22, WHITE, WIDTH / 2, HEIGHT / 2)
		self.draw_text("Press To Play", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
		self.draw_text("High Score: " + str(self.highscore), 22, WHITE, WIDTH / 2, 15)
		pygame.display.flip()
		self.wait_for_key()
		pygame.mixer.music.fadeout(500)

	# Game Over/Continue Screen
	def show_go_screen(self):
		if not self.running:
			return
		pygame.mixer.music.load(path.join(self.snd_dir, "Sad_Song.ogg"))
		pygame.mixer.music.play(loops = -1)
		self.screen.fill(LIGHTBLUE)
		self.draw_text("GAME OVER", 48, WHITE, WIDTH / 2, HEIGHT / 4)
		self.draw_text("Score: " + str(self.score), 22, WHITE, WIDTH / 2, HEIGHT / 2)
		self.draw_text("Press To Play Again", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
		if self.score > self.highscore:
			self.highscore = self.score
			self.draw_text("New High Score!", 22, WHITE, WIDTH / 2, HEIGHT / 2 + 40)
			with open(path.join(self.dir, HS_FILE), 'w') as f:
				f.write(str(self.score))
		else:
			self.draw_text("High Score: " + str(self.highscore), 22, WHITE, WIDTH / 2, HEIGHT / 2 + 40)
		pygame.display.flip()
		self.wait_for_key()
		pygame.mixer.music.fadeout(500)

	# Waiting Function
	def wait_for_key(self):
		waiting = True
		while waiting:
			self.clock.tick(FPS)
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					waiting = False
					self.running = False
				if event.type == pygame.KEYUP:
					waiting = False

	# Text Function
	def draw_text(self, text, size, color, x, y):
		font = pygame.font.Font(self.font_name, size)
		text_surface = font.render(text, True, color)
		text_rect = text_surface.get_rect()
		text_rect.midtop = (x, y)
		self.screen.blit(text_surface, text_rect)

g = Game()
g.show_start_screen()
while g.running:
	g.new()
	g.show_go_screen()

pygame.quit()