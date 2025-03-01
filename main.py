import pygame, pickle
from pygame.locals import *
from pygame import mixer 
from os import path
import sys

if getattr(sys, 'frozen', False):  
    BASE_PATH = sys._MEIPASS  
else:
    BASE_PATH = path.dirname(__file__)

# sound fx
pygame.mixer.pre_init(44100, -16, 2, 2048)
mixer.init()
pygame.init()

# main variables
s_w,s_h = 512,512
screen = pygame.display.set_mode((s_w,s_h))
pygame.display.set_caption("simple one bit platformer")
font_path = path.join(BASE_PATH, "font", "boxel.otf")
font = pygame.font.Font(font_path, 27)
clock = pygame.time.Clock()
fps = 60
t_s = 32
game_over = 0
level = 1
max_levels = 7
score = 0 

# load sounds
music_path = path.join(BASE_PATH, "sfx", "music.mp3")
pygame.mixer.music.load(music_path)
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1,0.0,7500)

coin_fx = pygame.mixer.Sound(path.join(BASE_PATH, "sfx", "coin.mp3"))
coin_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound(path.join(BASE_PATH, "sfx", "jump.mp3"))
jump_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound(path.join(BASE_PATH, "sfx", "game_over.mp3"))
game_over_fx.set_volume(0.5)

# load images
restart_button_img = pygame.image.load(path.join(BASE_PATH, "img", "buttons", "restart_button.png"))
restart_button_image = pygame.transform.scale(restart_button_img,(352,96))
start_button_img = pygame.image.load(path.join(BASE_PATH, "img", "buttons", "start_button.png"))
start_button_image = pygame.transform.scale(start_button_img,(256,96))
exit_button_img = pygame.image.load(path.join(BASE_PATH, "img", "buttons", "exit_button.png"))
exit_button_image = pygame.transform.scale(exit_button_img,(256,96))

# game state image
you_won_img = pygame.image.load(path.join(BASE_PATH, "img", "menu", "you_won.png"))
you_won_image = pygame.transform.scale(you_won_img,(336,64))
you_lost_img = pygame.image.load(path.join(BASE_PATH, "img", "menu", "you_lost.png"))
you_lost_image = pygame.transform.scale(you_lost_img,(368,64))

def reset_level(level):
    player.reset(32, s_h-128)
    enemy_group.empty()
    platform_group.empty()
    spike_group.empty()
    door_group.empty()
    coin_group.empty()

    level_path = path.join(BASE_PATH, f"levels", f"level{level}")
    if path.exists(level_path):
        with open(level_path, "rb") as pickle_in:
            world_data = pickle.load(pickle_in)
        world = World(world_data)

    return world

def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img,(x,y))

class Button():
    def __init__(self,x,y,image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False
        key = pygame.key.get_pressed()
        pos = pygame.mouse.get_pos()

        # check mouseover and clicked conditions 
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if key[pygame.K_r] and self.clicked == False:
            action = True
            self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        screen.blit(self.image, self.rect)
        return action

class ToggleButton():
    def __init__(self, x, y, images):
        self.images = images  # List of two images (ON and OFF)
        self.state = 0  # 0 = ON, 1 = OFF
        self.image = self.images[self.state]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.clicked = False

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()

        # Check if button is clicked
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # Draw the button
        screen.blit(self.image, self.rect)
        return action

    def toggle(self):
        self.state = 1 - self.state  # Toggle between 0 and 1
        self.image = self.images[self.state]

class Player():
    def __init__(self, x,y):
        self.reset(x, y)
        self.death_count = 0

    def update(self, game_over):
        dx, dy = 0, 0
        walk_cooldown = 5
        col_thresh = 4

        key = pygame.key.get_pressed()
        
        if game_over == 0:
            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                jump_fx.play()
                self.vel_y = -16
                self.jumped = True
            elif key[pygame.K_w] and self.jumped == False and self.in_air == False:
                jump_fx.play()
                self.vel_y = -16
                self.jumped = True
            elif key[pygame.K_UP] and self.jumped == False and self.in_air == False:
                jump_fx.play()
                self.vel_y = -16
                self.jumped = True
            if key[pygame.K_SPACE] == False:
                self.jumped = False
            elif key[pygame.K_w] == False:
                self.jumped = False
            elif key[pygame.K_UP] == False:
                self.jumped = False

            if key[pygame.K_a]:
                dx -= 4
                self.counter += 1
                self.direction = -1
            elif key[pygame.K_LEFT]:
                dx -= 4
                self.counter += 1
                self.direction = -1
            if key[pygame.K_d]:
                dx += 4
                self.counter += 1
                self.direction = 1
            elif key[pygame.K_RIGHT]:
                dx += 4
                self.counter += 1
                self.direction = 1
            if not key[pygame.K_a] and not key[pygame.K_d] and not key[pygame.K_LEFT] and not key[pygame.K_RIGHT]:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]
            
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1 
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]


            self.vel_y += 1
            if self.vel_y > 16:
                self.vel_y = 16
            dy += self.vel_y

            # check for collisions 
            self.in_air = True
            for tile in world.tile_list:
                # x direction
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # y direction collision 
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # check if below ground when jumping 
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    #check if above the ground when falling
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0 
                        self.in_air = False
            
            # check for collisions with enemies 
            if pygame.sprite.spritecollide(self, enemy_group, False):
                game_over_fx.play()
                game_over = -1
                self.death_count += 1
                # print(game_over)

            # check for collisions with spike 
            if pygame.sprite.spritecollide(self, spike_group, False):
                game_over_fx.play()
                game_over = -1
                self.death_count += 1
                # print(game_over)

            # check for collisions with door 
            if pygame.sprite.spritecollide(self, door_group, False):
                game_over = 1
                # print(game_over)

            # check for collisions with platforms
            for platform in platform_group:
                # collision in the x direction
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # collision in the y direction
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # check if below platform
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = (platform.rect.bottom - self.rect.top)
                    # check if above platform
                    elif abs((self.rect.bottom + dy) - platform.rect.top) > col_thresh:
                        self.rect.bottom = platform.rect.top - 1
                        self.in_air = False
                        dy = 0
                    # move sideways with the platform
                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction

                    if platform.move_y != 0:
                        self.rect.y += platform.move_direction

            self.rect.x += dx
            self.rect.y += dy

        screen.blit(self.image, self.rect)
        # pygame.draw.rect(screen,('white'), self.rect, 1)
        return game_over

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(0, 4):
            img_path = path.join(BASE_PATH, "img", "player", f"player{num}.png")
            img_right = pygame.image.load(img_path)
            img_right = pygame.transform.scale(img_right, (28, 28))
            img_left = pygame.transform.flip(img_right, True, False)

            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0 
        self.jumped = False
        self.direction = 0 
        self.in_air = True

class World():
    def __init__(self, data):
        self.tile_list = []
        wall_img = pygame.image.load(path.join(BASE_PATH, "img", "tiles", "wall.png"))
        
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(wall_img,(t_s,t_s))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * t_s
                    img_rect.y = row_count * t_s
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    spike = Spike(col_count * t_s, row_count * t_s)
                    spike_group.add(spike)
                if tile == 3:
                    door = Door(col_count * t_s, row_count * t_s)
                    door_group.add(door)
                if tile == 4:
                    coin = Coin(col_count * t_s, row_count * t_s)
                    coin_group.add(coin)
                if tile == 5:
                    enemy = Enemy(col_count * t_s, row_count * t_s)
                    enemy_group.add(enemy)
                if tile == 7:
                    moving_platform_x = Platform(col_count * t_s, row_count * t_s, 0, 1, 'y')
                    platform_group.add(moving_platform_x)
                if tile == 6:
                    moving_platform_y = Platform(col_count * t_s, row_count * t_s, 1, 0, 'x')
                    platform_group.add(moving_platform_y)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0],tile[1])
            # pygame.draw.rect(screen,('white'), tile[1], 1)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load(path.join(BASE_PATH, "img", "tiles", "enemy.png"))
        self.image = pygame.transform.scale(self.image,(t_s,t_s))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 32:
            self.move_direction *= -1
            self.move_counter *= -1

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y, direction):
        super().__init__()
        img_path = path.join(BASE_PATH, "img", "tiles", f"moving_platform_{direction}.png")
        img = pygame.image.load(img_path)
        self.image = pygame.transform.scale(img, (t_s, t_s // 4))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_counter = 0
        self.move_direction = 1
        self.move_x = move_x
        self.move_y = move_y

    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > 32:
            self.move_direction *= -1
            self.move_counter *= -1

class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        img = pygame.image.load(path.join(BASE_PATH, "img", "tiles", "spike.png"))
        self.image = pygame.transform.scale(img,(t_s,t_s))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        img = pygame.image.load(path.join(BASE_PATH, "img", "tiles", "coin.png"))
        self.image = pygame.transform.scale(img,(t_s,t_s))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Door(pygame.sprite.Sprite):
    def __init__(self, x, y,):
        super().__init__()
        img = pygame.image.load(path.join(BASE_PATH, "img", "tiles", "door.png"))
        self.image = pygame.transform.scale(img,(t_s,t_s))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

player = Player(32, s_h-32)

enemy_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
spike_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
door_group = pygame.sprite.Group()

level_path = path.join(BASE_PATH, f"levels", f"level{level}")
if path.exists(level_path):
    with open(level_path, "rb") as pickle_in:
        world_data = pickle.load(pickle_in)
    world = World(world_data)

# buttons
restart_button_new = Button(84, 222, restart_button_image)
start_button_new = Button(128, 96, start_button_image)
exit_button_new = Button(128, 208, exit_button_image)

# music & sound buttons 
music_images = [
    pygame.image.load(path.join(BASE_PATH, "img", "buttons", "music_on.png")),
    pygame.image.load(path.join(BASE_PATH, "img", "buttons", "music_off.png"))
]
music_images = [pygame.transform.scale(img, (120, 96)) for img in music_images]

sound_images = [
    pygame.image.load(path.join(BASE_PATH, "img", "buttons", "sound_on.png")),
    pygame.image.load(path.join(BASE_PATH, "img", "buttons", "sound_off.png"))
]
sound_images = [pygame.transform.scale(img, (120, 96)) for img in sound_images]

# Create Toggle Buttons
music_button = ToggleButton(128, 320, music_images)
sound_button = ToggleButton(264, 320, sound_images)


main_menu = True
run = True
while run:
    clock.tick(fps)

    if main_menu == True:
        # menu with buttons
        if start_button_new.draw():
            main_menu = False
        if exit_button_new.draw():
            run = False

        # code for my convinience    
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    main_menu = False
                if event.key == pygame.K_q:
                    run = False

        # Handle music toggle
        if music_button.draw():
            music_button.toggle()
            if music_button.state == 0:
                pygame.mixer.music.play(-1, 0.0, 7500)
            else:
                pygame.mixer.music.stop()

        # Handle sound toggle
        if sound_button.draw():
            sound_button.toggle()
            if sound_button.state == 0:
                coin_fx.set_volume(0.5)
                jump_fx.set_volume(0.5)
                game_over_fx.set_volume(0.5)
            else:
                coin_fx.set_volume(0)
                jump_fx.set_volume(0)
                game_over_fx.set_volume(0)
    else:
            
        screen.fill(('black'))
        world.draw()

        if game_over == 0:
            enemy_group.update()
            platform_group.update()
            if pygame.sprite.spritecollide(player, coin_group, True):
                coin_fx.play()
                score += 1
            draw_text('DEATH: X'+ str(player.death_count), font, 'white', 288, 32)
            draw_text('COINS: X'+ str(score), font, 'white', 32, 32)

        coin_group.draw(screen)
        enemy_group.draw(screen)
        spike_group.draw(screen)
        platform_group.draw(screen)
        door_group.draw(screen)
        
        game_over = player.update(game_over)

        if game_over == -1:
            screen.fill('black')

            # show you lost image
            screen.blit(you_lost_image, (72, 144))

            # restart button
            if restart_button_new.draw():
                player.reset(48, 480)
                game_over = 0

            draw_text(f"DEATH X{player.death_count}", font, 'white', 176, 328)            

        if game_over == 1:
            level += 1 
            if level <= max_levels:
                # reset level
                world_data = []
                world = reset_level(level)
                game_over = 0 
            else:
                # restart game
                screen.fill('black')

                # show you won image
                screen.blit(you_won_image, (88,128))

                draw_text(f"SCORE X{score}", font, 'white', 176, 320)
                draw_text(f"DEATH X{player.death_count}", font, 'white', 176, 352)
                if restart_button_new.draw():
                    level = 1 
                    world_data = []
                    world = reset_level(level)
                    game_over = 0 
                    score = 0
                    player.death_count = 0
                    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                run = False
    
    pygame.display.update()

pygame.quit()