import pygame
import pickle
from os import path
pygame.init()

clock = pygame.time.Clock()
fps = 60

# game window
t_s = 32
cols = 16
margin = 64
s_w = t_s * cols
s_h = (t_s * cols) + margin
screen = pygame.display.set_mode((s_w, s_h))
pygame.display.set_caption('Level Editor')
bg_img = pygame.Surface((512,512))
bg_img.fill('black')
# define game variables
clicked = False
level = 1
font = pygame.font.Font("font/boxel.otf", 21)

# import images
wall_img = pygame.image.load('img/tiles/wall.png')
wall_image = pygame.transform.scale(wall_img,(t_s,t_s))
spike_img = pygame.image.load('img/tiles/spike.png')
spike_image = pygame.transform.scale(spike_img,(t_s,t_s))
door_img = pygame.image.load('img/tiles/door.png')
door_image = pygame.transform.scale(door_img,(t_s,t_s))
coin_img = pygame.image.load('img/tiles/coin.png')
coin_image = pygame.transform.scale(coin_img,(t_s,t_s))
enemy_img = pygame.image.load('img/tiles/enemy.png')
enemy_image = pygame.transform.scale(enemy_img,(t_s,t_s))
moving_platform_x_img = pygame.image.load('img/tiles/moving_platform_x.png')
moving_platform_x_image = pygame.transform.scale(moving_platform_x_img,(t_s,t_s))
moving_platform_y_img = pygame.image.load('img/tiles/moving_platform_y.png')
moving_platform_y_image = pygame.transform.scale(moving_platform_y_img,(t_s,t_s))

# import button images
load_img = pygame.image.load('img/buttons/load.png')
load_image = pygame.transform.scale(load_img,(108,36))
save_img = pygame.image.load('img/buttons/save.png')
save_image = pygame.transform.scale(save_img,(108,36))


# create empty tile list
world_data = []
for row in range(16):
	r = [0] * 16
	world_data.append(r)

# create boundary
for tile in range(0, 16):
	world_data[15][tile] = 1
	world_data[0][tile] = 1
	world_data[tile][0] = 1
	world_data[tile][15] = 1

# function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

def draw_grid():
	for c in range(17):
		# vertical lines
		pygame.draw.line(screen, 'white', (c * t_s, 0), (c * t_s, s_h - margin))
		# horizontal lines
		pygame.draw.line(screen, 'white', (0, c * t_s), (s_w, c * t_s))

def draw_world():
	for row in range(16):
		for col in range(16):
			if world_data[row][col] > 0:
				if world_data[row][col] == 1:
					img = pygame.transform.scale(wall_image, (t_s, t_s))
					screen.blit(img, (col * t_s, row * t_s))
				if world_data[row][col] == 2:
					#spike
					img = pygame.transform.scale(spike_image, (t_s, t_s))
					screen.blit(img, (col * t_s, row * t_s))
				if world_data[row][col] == 3:
					#horizontally moving platform
					img = pygame.transform.scale(door_image, (t_s, t_s))
					screen.blit(img, (col * t_s, row * t_s))
				if world_data[row][col] == 4:
					#coin
					img = pygame.transform.scale(coin_image, (t_s,t_s))
					screen.blit(img, (col * t_s, row * t_s))
				if world_data[row][col] == 5:
					#enemy blocks
					img = pygame.transform.scale(enemy_image, (t_s,t_s))
					screen.blit(img, (col * t_s, row * t_s))
				if world_data[row][col] == 6:
					# moving platform
					img = pygame.transform.scale(moving_platform_x_image, (t_s, t_s//4))
					screen.blit(img, (col * t_s, row * t_s))
				if world_data[row][col] == 7:
					# moving platform
					img = pygame.transform.scale(moving_platform_y_image, (t_s, t_s//4))
					screen.blit(img, (col * t_s, row * t_s))

class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self):
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button
		screen.blit(self.image, (self.rect.x, self.rect.y))

		return action

#create load and save buttons
save_button = Button(s_w // 2 - 96, s_h - 64, save_image)
load_button = Button(s_w // 2 + 64, s_h - 64, load_image)

#main game loop
run = True
while run:

	clock.tick(fps)

	#draw background
	screen.fill('black')
	screen.blit(bg_img, (0, 0))

	#show the grid and draw the level tiles
	draw_grid()
	draw_world()
	#load and save level
	if save_button.draw():
		#save level data
		pickle_out = open(f'levels/level{level}', 'wb')
		pickle.dump(world_data, pickle_out)
		pickle_out.close()
	if load_button.draw():
		#load in level data
		if path.exists(f'levels/level{level}'):
			pickle_in = open(f'levels/level{level}', 'rb')
			world_data = pickle.load(pickle_in)

	#text showing current level
	draw_text(f'Level: {level}', font, 'white', t_s, s_h - 56)
	draw_text('Press UP or DOWN to change level', font, 'white', t_s, s_h - 24)

	#event handler
	for event in pygame.event.get():
		#quit game
		if event.type == pygame.QUIT:
			run = False
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_q:
				run = False
		#mouseclicks to change tiles
		if event.type == pygame.MOUSEBUTTONDOWN and clicked == False:
			clicked = True
			pos = pygame.mouse.get_pos()
			x = pos[0] // t_s
			y = pos[1] // t_s
			#check that the coordinates are within the tile area
			if x < 16 and y < 16:
				#update tile value
				if pygame.mouse.get_pressed()[0] == 1:
					world_data[y][x] += 1
					if world_data[y][x] > 7:
						world_data[y][x] = 0
				elif pygame.mouse.get_pressed()[2] == 1:
					world_data[y][x] -= 1
					if world_data[y][x] < 0:
						world_data[y][x] = 7
		if event.type == pygame.MOUSEBUTTONUP:
			clicked = False
		#up and down key presses to change level number
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_UP:
				level += 1
			elif event.key == pygame.K_DOWN and level > 1:
				level -= 1

	#update game display window
	pygame.display.update()

pygame.quit()