import pygame
import data
import time
import numpy as np
import os
import random
import pandas as pd
import inspect
import asyncio
import math

from pygame.examples.music_drop_fade import SCREEN_SIZE
# Import buttons
from pygame.locals import (KEYDOWN, QUIT, KEYUP, K_LCTRL,
    K_UP, K_DOWN, K_LEFT, K_RIGHT, K_ESCAPE, K_TAB, K_LSHIFT, K_SPACE,
    K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9, K_0,
                           K_q, K_w, K_e, K_r, K_t,
                           K_a, K_s, K_d, K_f, K_g,
                           K_z, K_x, K_c, K_v, K_b)

# Screen settings
resolution = 1             # Set window size; 16:9 ratio .8-720p .6-540p .5~480p
SCREEN_SIZE = [int(1280 * resolution), int(800 * resolution)]
screen = pygame.display.set_mode([SCREEN_SIZE[0], SCREEN_SIZE[1]])

running = True
keys_pressed = set()
clock = pygame.time.Clock()
framerate = 60; dt = 0      # Makes time-based calculations relative to framerate
# pygame.mouse.set_visible(False)     # Hide mouse cursor

# Initialize PyGame
pygame.init()
pause = False
true_counter = 0
realtime = 0
frame_counter = 0
mouse_pos = pygame.mouse.get_pos()

Fonts = {}
fsizes = range(10, 70, 5)

# Fonts
for i in fsizes:
    Fonts[f"mono{i}b"] = pygame.font.SysFont("Mono", i, bold=True)
    Fonts[f"mono{i}"] = pygame.font.SysFont("Mono", i, bold=False)
    Fonts[f"helv{i}b"] = pygame.font.SysFont("Helvetica", i, bold=True)
    Fonts[f"helv{i}"] = pygame.font.SysFont("Helvetica", i, bold=False)

# Load colors
Colors = {'red': (255, 0, 0), 'green': (0, 255, 0), 'blue': (0, 0, 255), 'white': (255, 255, 255),
          'yellow': (255, 255, 0), 'orange': (255, 150, 0), 'pink': (255, 0, 150),
          'purple': (150, 0, 255), 'cyan': (0, 255, 255), 'teal': (0, 150, 255),
          'lime': (150, 255, 0), 'seafoam': (0, 255, 150), 'magenta': (255, 0, 255)}

class Fighter():
    def __init__(self, name):
        self.name = name
        self.HP = 1
        self.ATK = 1
        self.DEF = 1
        self.WIS = 1
        self.AGI = 1
        self.LV = 1
        self.SEF = 0
        self.rarity = 'Common'
        self.tribe = 'null'
        self.sign = 'null'
        self.type = 'null'

empty = Fighter('-')

band = np.array([[empty,] * 3]*3)
band_pos = np.array([[[0]*2] * 3]*3)
hp_band = np.array([[0,] * 3]*3)
space = 160
bx = 100
by = 200
enemies_pos = np.array([[0]*2] * 3)
for x in range(3):
    enemies_pos[x] = [SCREEN_SIZE[0] - 300, by + 30 + space * x]
    for y in range(3):
        xx = bx + 30 + space * x
        yy = by + 30 + space * y
        band_pos[x][y] = [xx, yy]

home_pos = band_pos
front_pos = (home_pos[2][0][0] + 200, home_pos[2][0][1])

enemies = np.array([empty,] * 3)
frontline = [0, 0, 0]

barracks = {}
attack_order = {}
queue = 0
attack_counter = 0
attack_timer = 0
swipe_order = [0,]

# // FUNCTIONS //
def draw_text(text, font, text_col, x, y):  # Function for outputting text onto the screen
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

Portrait = {}

def image(name):
    name = pygame.image.load(f"lib/fighters/{name}_Sprite.webp")
    return name

swipe_list = (K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8)
def swipe(pressed):
    if pressed == K_1:
        return band[0]
    if pressed == K_2:
        return band[1]
    if pressed == K_3:
        return band[2]
    if pressed == K_4:
        return band[:, 0]
    if pressed == K_5:
        return band[:, 1]
    if pressed == K_6:
        return band[:, 2]
    if pressed == K_7:
        tmp = [0, 0, 0]
        for n in range(3):
            tmp[n] = band[n][n]
        return tmp
    if pressed == K_8:
        tmp = [0, 0, 0]
        for n in range(3):
            tmp[n] = band[2 - n][n]
        return tmp

# Images
background = pygame.image.load(f"lib/images/background.png")
sz = background.get_size()
scl = SCREEN_SIZE[0] / sz[0]
background = pygame.transform.scale(background, (sz[0] * scl, sz[1] * scl))

Icon = {}
list = ['fight', 'journey', 'build', 'begin']
for n in list:
    Icon[n] = pygame.image.load(f"lib/images/{n}.png")

# ODS Import code
file_path = 'db_texel.ods'
db_fighters = pd.read_excel(file_path, engine='odf', sheet_name=1) # Import sheet 2
db_rows = db_fighters.index.size
db_columns = db_fighters.columns.size
fighter_dict = {}

for n in range(db_columns):
    if n % 4 != 0:
        fighter_dict[db_fighters.columns[n]] = db_fighters.iloc[0, n]

fighters = list(fighter_dict.keys())
num_fighters = len(fighters)
common_pack = ['Fodder'] * 90 + ['Bronze Fodder'] * 6 + ['Silver Fodder'] * 3 + ['Gold Fodder'] * 1
uncommon_pack = []
rare_pack = []
epic_pack = []
legendary_pack = []
for n in range(num_fighters):
    name = fighters[n]
    if fighter_dict[name] == 'Uncommon':
        uncommon_pack = list(uncommon_pack) + [name]
    elif fighter_dict[name] == 'Rare':
        rare_pack = list(rare_pack) + [name]
    elif fighter_dict[name] == 'Epic':
        epic_pack = list(epic_pack) + [name]
    elif fighter_dict[name] == 'Legendary':
        legendary_pack = list(legendary_pack) + [name]

class Button():    # Function for clickable buttons on screen
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.clicked = False  # used for singles button clicks

    def draw(self):
        action = False
        # Mouse over event
        mousepos = pygame.mouse.get_pos()

        if self.rect.collidepoint(mousepos):  # Over button
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:  # Left click
                self.clicked = True
                action = True

        # Draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action

    def hover(self):
        action = False# Mouse over event
        mousepos = pygame.mouse.get_pos()

        if self.rect.collidepoint(mousepos):  # Over button
            action = True

        return action


def colorize(photo, newColor):
    photo = photo.copy()
    photo.fill((0, 0, 0, 100), None, pygame.BLEND_RGBA_MULT)
    photo.fill(newColor[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)

    return photo


def open(box):
    if box == 'Common':
        value = random.choice(common_pack)
    elif box == 'Uncommon':
        value = random.choice(uncommon_pack)
    elif box == 'Rare':
        value = random.choice(rare_pack)
    elif box == 'Epic':
        value = random.choice(epic_pack)
    elif box == 'Legendary':
        value = random.choice(legendary_pack)

    return value

LeftHold = False
LeftClick = False
fight = False
strike = False
strike_hold = False
spawn_state = True
fight_start = False

while running:
    # CONTROLS
    for event in pygame.event.get():
        # Reading Keyboard Input
        if event.type == KEYDOWN:
            keys_pressed.add(event.key)
            if len(swipe_order) <= 3:
                if event.key in swipe_list and event.key not in swipe_order:
                    frontline = swipe(event.key)
                    swipe_order = list(swipe_order) + [event.key]
        if event.type == pygame.QUIT or K_ESCAPE in keys_pressed:
            running = False
        # Reading Mouse Input
        if event.type == pygame.MOUSEWHEEL:
            if event.y == 1:
                wheel_up = True
            if event.y == -1:
                wheel_down = True
        if pygame.mouse.get_pressed()[0] and not LeftHold:	    # Left Click
            LeftClick = True
            LeftHold = True
            ClickBubble = True
            Bubble_xy = mouse_pos
            HoldStart = true_counter
            bubble_counter = true_counter
        if pygame.mouse.get_pressed()[2] and not RightClick:	# Right Click
            RightClick = True
        if pygame.mouse.get_pressed()[1] and not MiddleClick:	# Middle Click
            MiddleClick = True
 
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                LeftClick = False
                LeftHold = False
                HoldTime = (true_counter - HoldStart) / framerate
                buttoncheck = False
                clock_hold = False
                zero_hold = False
            if event.button == 2:
                MiddleClick = False
            if event.button == 3:
                RightClick = False
        if event.type == pygame.KEYUP:
            if event.key in keys_pressed:
                keys_pressed.remove(event.key)

    # Draw Screen
    screen.fill((5, 5, 10))
    screen.blit(background, (0, -200))

    if main_menu:
        if Button(SCREEN_SIZE[0]/2, SCREEN_SIZE[1] - 50, Icon['journey'], 1).draw():
            journey_menu = True
        if Button(200, SCREEN_SIZE[1] - 50, Icon['build'], 1).draw():
            build_menu = True

    if journey_menu:
        main_menu = False
        if Button(SCREEN_SIZE[0]/2, SCREEN_SIZE[1] - 50, Icon['begin'], 1).draw():
            journey_start = True
            journey_timer = 0
            num_fights = random.choice(range(1, 4))
            
    if build_menu:
        main_menu = False
        if Button(SCREEN_SIZE[0]/2, SCREEN_SIZE[1] - 50, Icon['build-pixite'], 1).draw():
            build_state = True
            build_pixite = True
        if Button(SCREEN_SIZE[0]/2, SCREEN_SIZE[1] - 50, Icon['build-voxite'], 1).draw():
            build_state = True
            build_pixite = True
            build_voxite = True
        if Button(SCREEN_SIZE[0]/2, SCREEN_SIZE[1] - 50, Icon['build-doxite'], 1).draw():
            build_state = True
            build_doxite = True
        if Button(SCREEN_SIZE[0]/2, SCREEN_SIZE[1] - 50, Icon['build-texite'], 1).draw():
            build_state = True
            build_texite = True
            
    if build_state:
        if build_pixite:
            z = ['Uncommon', 10, 5] * 5 + ['Common', 1, 1] * 3
        if build_voxite:
            z = [['Uncommon', 10, 5]] * 5 + [['Rare', 20, 10]] * 3
        if build_doxite:
            z = [['Uncommon', 10, 5]] * 5 + [['Rare', 20, 10]] * 3 + [['Epic', 30, 15]] * 2
        if build_texite:
            z = [['Rare', 20, 10]] * 3 + [['Epic', 30, 15]] * 2 + [['Legendary', 50, 25]]
        for n in range(len(z)):
            z_n = z[n]
            pick = open(z_n[0])
            before = pick
            while pick in barracks.keys():
                p = 1
                pick = f"{pick}-{p}"
                p += 1
            barracks[pick] = Fighter(before)
            barracks[pick].HP = random.choice(range(1, z_n[1]+1))
            barracks[pick].ATK = random.choice(range(1, z_n[1]+1))
            barracks[pick].DEF = random.choice(range(1, z_n[1]+1))
            barracks[pick].WIS = random.choice(range(1, z_n[2]+1))
            barracks[pick].AGI = random.choice(range(1, z_n[2]+1))
            Portrait[before] = image(before)

    if journey_start:
        # Draw journey background
        if not encounter:
            journey_timer += dt
        if journey_timer >= (3 / num_fights + random.choice(0, 10) / 10):
            encounter = True
            enemy_power = 0
            for x in range(3):
                pick = open('Uncommon')
                enemies[x] = Fighter(pick)
                Portrait[pick] = image(pick)
                enemies[x].HP = random.choice(range(30, 100))
                enemies[x].ATK = random.choice(range(1, 10))
                enemy_power += enemies[x].ATK
        if encounter:
            # Draw enemies
            if Button(50, 50, Icon['fight'], 1).draw():
                fight_start = True
        
    if fight_start:
        fight = True
        fight_start = False
        overkill = 0
        spawn_state = True
        # Temporary band setup, remove once menus work
        xyz = list(barracks)
        for x in range(3):
            for y in range(3):
                index = x * 3 + y
                band[x][y] = barracks[xyz[index]] # Automatically assign band of fighter

    if fight:
        s = pygame.Surface((540, 545), pygame.SRCALPHA)
        s.fill((25, 25, 25, 100))
        screen.blit(s, (bx, by))
        for x in range(3):
            if enemies[x].HP > 0 and not spawn_state:
                enemy_hp = enemies[x].HP
                q = len(f"{enemy_hp}")
                villain = Portrait[enemies[x].name]
                villain = pygame.transform.flip(villain, True, False)
                enemy_portrait = colorize(villain, Colors['red'])
                rectangle = pygame.Rect(enemies_pos[0][0], 220 + space * x, 100, 15)
                pygame.draw.rect(screen, Colors['red'], rectangle)
                draw_text(f"{enemy_hp} HP", Fonts['helv10'], Colors['white'],
                          enemies_pos[0][0] + 3, 223 + space * x)
                screen.blit(villain, enemies_pos[x])
                screen.blit(enemy_portrait, enemies_pos[x])
            for y in range(3):
                pick = band[x][y]
                pos = band_pos[x][y]
                hp_band[x][y] = pick.HP
                screen.blit(Portrait[pick.name], pos)
                draw_text(f"LV {pick.LV}", Fonts['helv15b'], Colors['orange'], pos[0] + 25, pos[1] + 125)
                draw_text(f"{pick.ATK} ATK", Fonts['helv15b'], Colors['red'], pos[0] + 90, pos[1] + 125)

        total_health = np.array([0, 0, 0])
        for n in range(3):
            total_health[n] = enemies[n].HP

        if np.sum(total_health) == 0:
            spawn_state = True 

        # Swipe selections
        swipe_colors = [Colors['yellow'], Colors['orange'], Colors['red']]
        for x in range(len(swipe_order)-1):
            rectangle = pygame.Rect(-50, -50, 10, 10)
            index = x+1
            if list(swipe_order)[index] == K_1:
                rx = band_pos[0][0][0]
                ry = band_pos[0][0][1]
                rectangle = pygame.Rect(rx - 5, ry - 15, space + 5, space * 3 + 15)
            elif list(swipe_order)[index] == K_2:
                rx = band_pos[1][0][0]
                ry = band_pos[1][0][1]
                rectangle = pygame.Rect(rx - 5, ry - 15, space + 5, space * 3 + 15)
            elif list(swipe_order)[index] == K_3:
                rx = band_pos[2][0][0]
                ry = band_pos[2][0][1]
                rectangle = pygame.Rect(rx - 5, ry - 15, space + 5, space * 3 + 15)
            elif list(swipe_order)[index] == K_4:
                rx = band_pos[0][0][0]
                ry = band_pos[0][0][1]
                rectangle = pygame.Rect(rx-10, ry-10, space * 3 + 20, space + 5)
            elif list(swipe_order)[index] == K_5:
                rx = band_pos[0][1][0]
                ry = band_pos[0][1][1]
                rectangle = pygame.Rect(rx-10, ry-10, space * 3 + 20, space + 5)
            elif list(swipe_order)[index] == K_6:
                rx = band_pos[0][2][0]
                ry = band_pos[0][2][1]
                rectangle = pygame.Rect(rx-10, ry-10, space * 3 + 20, space + 5)
            elif list(swipe_order)[index] == K_7:
                rx = band_pos[0][0][0]
                ry = band_pos[0][0][1] + 10
                vertices = [(rx-35, ry+space/2), (rx + space/2, ry - 35),
                            (rx + space*3.2, ry + space*2.5), (rx + space*2.5, ry + space*3.2)]
                pygame.draw.polygon(screen, swipe_colors[x], vertices, 4)  # Draw the polygon
            elif list(swipe_order)[index] == K_8:
                rx = band_pos[2][0][0] + space - 4
                ry = band_pos[2][0][1] + 8
                vertices = [(rx + 35, ry + space / 2), (rx - space / 2, ry - 35),
                            (rx - space * 3.2, ry + space * 2.5), (rx - space * 2.5, ry + space * 3.2)]
                pygame.draw.polygon(screen, swipe_colors[x], vertices, 4)  # Draw the polygon

            pygame.draw.rect(screen, swipe_colors[x], rectangle, 4)

        if frontline[0] != 0:
            attack_order[queue] = frontline
            frontline = [0, 0, 0]
            damage = [0, 0, 0]
            queue += 1

        if queue == 3:    # Attack animations
            power = 0
            t1 = 0.6
            t2 = 0.82
            t3 = 1.6
            speed = 1300
            if t1 < attack_timer <= t2:
                xx = front_pos[0] + (attack_timer-t1) * speed
            elif t2 < attack_timer <= t3:
                strike = True
                xx = front_pos[0] + (t2 - t1) * speed - (attack_timer-t2) * 400
                for j in range(3):
                    draw_text(f"-{damage[j]}", Fonts['helv30b'], Colors['orange'], enemies_pos[0][0] - 20, enemies_pos[0][1] + space * j
                if xx < front_pos[0]:
                    xx = front_pos[0]
            else:
                xx = front_pos[0]
            for y in range(3):
                k = attack_counter
                screen.blit(Portrait[attack_order[k][y].name], (xx, front_pos[1] + space*y))
                power += attack_order[k][y].ATK
            if strike and not strike_hold:
                for j in range(3):
                    modifier = 1
                    crit_chance = 100
                    if 1 == random.choice(range(crit_chance)):
                        modifier = 10
                    damage[j] = power * modifier
                    enemies[j].HP -= damage[j]
                    if enemies[j].HP < 0:
                        overkill -= enemies[j].HP
                        enemies[j].HP = 0
                strike_hold = True
                strike = False
            if attack_timer >= 2:
                attack_counter += 1
                attack_timer = 0
                strike_hold = False
                strike = False
            else:
                attack_timer += dt
            if attack_counter == 3:
                enemy_attack = True
            if enemy_attack and attack_timer > t1:
                hp_band -= enemy_power
                enemy_attack = False
                enemy_done - True
            elif enemy_done and attack_timer > t3:
                queue = 0
                attack_counter = 0
                attack_order = {}
                swipe_order = [0,]

    pygame.display.update()
    dt = clock.tick(framerate) / 1000	# Makes movement or time-related events work independent of framerate
    if not pause:
        true_counter += dt 	# Total time game has been unpaused
    if true_counter >= 2:   # Allow timedd for game to load
        startup_state = False
    realtime += dt  # Total play time
    frame_counter += 1     	# Total number of rendered frames
    # ~~~~~ End of game loop ~~~~~

pygame.quit()
