import pygame

# Constant Variables
TITLE = "Game"
WIDTH = 480
HEIGHT = 600
FPS = 60
vec = pygame.math.Vector2
FONT_NAME = "arial"
HS_FILE = "HighScore.txt"
SPRITESHEET = "spritesheet_jumper.png"

# Player Properties
PLAYER_ACC = 0.5
PLAYER_FRICTION = -0.12
PLAYER_GRAV = 0.8
PLAYER_JUMP = 22

# Game Properties
BOOST_POWER = 60
POW_SPAWM_FREQUENCY = 10
MOB_FREQUENCY = 5000
PLAYER_LAYER = 2
PLATFORM_LAYER = 1
MOB_LAYER = 2
POWER_LAYER = 1
CLOUD_LAYER = 0

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
LIGHTBLUE = (0, 155, 155)

# Starting Platforms (x-coordinate, y-coordinate, Width Of The Platform, Thickness)
PLATFORM_LIST = [
	(0, HEIGHT - 60), 
	(WIDTH / 2 - 50, HEIGHT * 3 / 4 - 50),
	(125, HEIGHT - 350),
	(350, 200),
	(175, 100)
]