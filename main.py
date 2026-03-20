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
          'lime': (150, 255, 0), 'seafoam': (0, 255, 150), 'magenta': (255, 0, 255),
          'gold': (255, 215, 0)}

class Fighter():
    def __init__(self, name, keyname):
        self.name = name
        self.keyname = keyname
        self.HP = 0
        self.ATK = 0
        self.DEF = 0
        self.WIS = 0
        self.AGI = 0
        self.LV = 1
        self.SEF = 0
        self.XP = 0
        self.rarity = 'Common'
        self.tribe = 'null'
        self.sign = 'null'
        self.type = 'null'

empty = Fighter('-', 'empty')

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

Portrait['-'] = image('empty')

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
pic_list = ['fight', 'journey', 'build', 'begin', 'continue', 'build-pixite',
            'build-voxite', 'build-doxite', 'build-texite', 'band', 'check', 'fuse']
for n in pic_list:
    Icon[n] = pygame.image.load(f"lib/images/{n}.png")

sz = Icon['check'].get_size()
scl = 22
Icon['check'] = pygame.transform.scale(Icon['check'], (sz[0]/scl, sz[1]/scl))

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
common_pack = ['Fodder'] * 190 + ['Ikkupi'] * 10 + ['Banunu'] * 4 + ['Sirsir'] * 1
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

# Initialize Variables
fuse_type = 'self'
# Boolean
LeftHold = False
LeftClick = False
strike = False
strike_hold = False
encounter = False
victory = False
enemy_attack = False
enemy_done = False
attack_state = False
buttoncheck = False
RightClick = False
show_band = False
info_button = False


win_count = 0

game_state = 'main_menu'

dmg_color = [Colors['orange'], ] * 3

pixite = 12
voxite = 7
doxite = 1
texite = 0
build_pixite = False
build_voxite = False
build_doxite = False
build_texite = False

#debug
debug = True
if debug:
    game_state = 'band_sort'
    show_band = True
    fakeout = True
    pull = {}
    z = [['Uncommon', 10, 5]] * 5 + [['Common', 1, 1]] * 9
    z = z + [['Uncommon', 10, 5]] * 5 + [['Rare', 20, 10]] * 3
    z = z + [['Uncommon', 10, 5]] * 5 + [['Rare', 20, 10]] * 3 + [['Epic', 30, 15]] * 2
    for n in range(len(z)):
        z_n = z[n]
        pick = open(z_n[0])
        before = pick
        while pick in barracks.keys():
            p = 1
            pick = f"{pick}-{p}"
            p += 1
        barracks[pick] = Fighter(before, pick)
        barracks[pick].HP = random.choice(range(1, z_n[1]+1))
        if z[n] != 'Common':
            barracks[pick].HP += 9
        barracks[pick].ATK = random.choice(range(1, z_n[1]*2+1))
        barracks[pick].DEF = random.choice(range(1, z_n[1]+1))
        barracks[pick].WIS = random.choice(range(1, z_n[2]+1))
        barracks[pick].AGI = random.choice(range(1, z_n[2]+1))
        Portrait[before] = image(before)


while running:
    # CONTROLS
    mouse_pos = pygame.mouse.get_pos()
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

    if game_state == 'main_menu':
        stash = [pixite, voxite, doxite, texite]
        clr = [Colors['orange'], Colors['white'], Colors['yellow'], Colors['blue']]
        for p in range(4):
            draw_text(f"x{stash[p]}", Fonts['helv20b'], clr[p], 1100, 100 + 30 * p)
        if Button(SCREEN_SIZE[0]/2, SCREEN_SIZE[1] - 50, Icon['journey'], 1).draw() and not buttoncheck:
            buttoncheck = True
            game_state = 'journey_menu'
        if Button(200, SCREEN_SIZE[1] - 50, Icon['build'], 1).draw() and not buttoncheck:
            buttoncheck = True
            game_state = 'build_menu'
        if Button(900, SCREEN_SIZE[1] - 150, Icon['band'], 1).draw() and not buttoncheck:
            buttoncheck = True
            game_state = 'band_menu'
            band_init = True
        if 300 < mouse_pos[0] < 900 and 200 < mouse_pos[1] < 500:    # !! Make this the square that shows the band on the home screen
            if LeftClick:
                LeftClick = False
                game_state = 'band_setup'
                band_init = True
        if show_band:
            for x in range(3):
                for y in range(3):
                    pick = band[x][y]
                    pos = [band_pos[x][y][0] + 260, band_pos[x][y][1] - 160]
                    hp_tmp = hp_band[x][y]
                    screen.blit(Portrait[pick.name], pos)
                    draw_text(f"LV {pick.LV}", Fonts['helv15b'], Colors['orange'], pos[0] + 25, pos[1] + 125)
                    if info_button:
                        draw_text(f"ATK {pick.ATK}", Fonts['helv15b'], Colors['red'], pos[0] + 25, pos[1] + 95)

    if game_state == 'journey_menu':
        if Button(SCREEN_SIZE[0]/2, SCREEN_SIZE[1] - 250, Icon['begin'], 1).draw() and not buttoncheck:
            buttoncheck = True
            game_state = 'journey'
            journey_state = True 
            journey_timer = 0
            swipe_order = [0, ]
            win_count = 0
            num_fights = random.choice(range(1, 4))

    if game_state == 'band_menu':
        if RightClick:
            RightClick = False
            game_state = 'main_menu'
        b_keys = list(barracks.keys())
        barracks_size = len(b_keys)
        for n in range(barracks_size):  
            tmp = b_keys[n]
            pick = barracks[tmp]
            logo = Portrait[pick.name]
            columns = 7
            xx = 100 + space * 1.1 * (n % columns)
            yy = 100 * (1 + n // columns)
            if Button(xx, yy, logo, 1).draw():
                selection = pick
                game_state = 'fusion'
                fuse_setup = True
            info = [pick.name, pick.HP, pick.ATK, pick.DEF, pick.WIS, pick.AGI,
                    pick.LV, pick.SEF, pick.rarity]
            cat = ['', 'HP ', 'ATK', 'DEF', 'WIS', 'AGI', 'LV ', 'SEF', '']
            for j in range(len(info)):
                if j == 0:
                    y_text = yy - 10
                    font_a = Fonts['helv20b']
                else:
                    y_text = yy
                    font_a = Fonts['helv10b']
                x_text = xx - 50
                draw_text(f"{cat[j]} {info[j]}", font_a, Colors['white'], x_text, y_text + 18 * j)
            
    if game_state == 'build_menu':
        if RightClick:
            RightClick = False
            game_state = 'band_sort'
            fakeout = True
        if Button(200, 300, Icon['build-pixite'], 1).draw() and not buttoncheck:
            buttoncheck = True
            if pixite >= 5:
                pixite -= 5
                build_pixite = True
                game_state = 'build_state'
        if Button(200, SCREEN_SIZE[1] - 300, Icon['build-voxite'], 1).draw() and not buttoncheck:
            buttoncheck = True
            if voxite >= 5:
                voxite -= 5
                build_voxite = True
                game_state = 'build_state'
        if Button(SCREEN_SIZE[0] - 300, 300, Icon['build-doxite'], 1).draw() and not buttoncheck:
            buttoncheck = True
            if doxite >= 5:
                doxite -= 5
                build_doxite = True
                game_state = 'build_state'
        if Button(SCREEN_SIZE[0] - 300, SCREEN_SIZE[1] - 300, Icon['build-texite'], 1).draw() and not buttoncheck:
            buttoncheck = True
            if texite >= 5:
                texite -= 5
                build_texite = True
                game_state = 'build_state'

    if game_state == 'build_state':
        pull = {}
        if build_pixite:
            z = [['Uncommon', 10, 5]] * 5 + [['Common', 1, 1]] * 3
            build_pixite = False
        if build_voxite:
            z = [['Uncommon', 10, 5]] * 5 + [['Rare', 20, 10]] * 3
            build_voxite = False
        if build_doxite:
            z = [['Uncommon', 10, 5]] * 5 + [['Rare', 20, 10]] * 3 + [['Epic', 30, 15]] * 2
            build_doxite = False
        if build_texite:
            z = [['Rare', 20, 10]] * 3 + [['Epic', 30, 15]] * 2 + [['Legendary', 50, 25]]
            build_texite = False
        for n in range(len(z)):
            z_n = z[n]
            pick = open(z_n[0])
            before = pick
            while pick in barracks.keys():
                p = 1
                pick = f"{pick}-{p}"
                p += 1
            barracks[pick] = Fighter(before, pick)
            barracks[pick].HP = random.choice(range(1, z_n[1]+1))
            if z[n] != 'Common':
                barracks[pick].HP += 9
            barracks[pick].ATK = random.choice(range(1, z_n[1]+1))
            barracks[pick].DEF = random.choice(range(1, z_n[1]+1))
            barracks[pick].WIS = random.choice(range(1, z_n[2]+1))
            barracks[pick].AGI = random.choice(range(1, z_n[2]+1))
            Portrait[before] = image(before)
            pull[n] = barracks[pick]
        game_state = 'build_results'
        results_timer = 0
        num_display = 0
        num_total = len(pull.keys())

    if game_state == 'build_results':
        if num_display < num_total:
            results_timer += dt
            if results_timer >= 1:
                num_display += 1
        elif Button(SCREEN_SIZE[0]/2, SCREEN_SIZE[1] - 50, Icon['continue'], 1).draw() and not buttoncheck:
            buttoncheck = True
            game_state = 'build_menu'
        for n in range(num_display):
            pull_n = pull[n]
            logo_result = Portrait[pull_n.name]
            xx = 110 + space * 1.5 * (n % 5)
            yy = 70 + 230 * (n // 5)
            screen.blit(logo_result, (xx, yy))
            info = [pull_n.name, pull_n.HP, pull_n.ATK, pull_n.DEF, pull_n.WIS, pull_n.AGI,
                    pull_n.LV, pull_n.SEF, pull_n.rarity]
            cat = ['', 'HP ', 'ATK', 'DEF', 'WIS', 'AGI', 'LV ', 'SEF', '']
            for j in range(len(info)):
                if j == 0:
                    y_text = yy - 10
                    font_a = Fonts['helv25b']
                else:
                    y_text = yy
                    font_a = Fonts['helv15b']
                x_text = xx - 50
                draw_text(f"{cat[j]} {info[j]}", font_a, Colors['white'], x_text, y_text + 18 * j)

    if game_state == 'fusion':
        if RightClick:
            RightClick = False
            game_state = 'main_menu'
        # fusion mechanics
        if fuse_setup:
            fuse_list = []
            fuse_counter = 0
            if fuse_type == 'self':
                name_fuse = [selection.name]
            elif fuse_type == 'sacrifice':
                name_fuse = ['Fodder', 'Ikuppi', 'Banunu', 'Sirsir']
            b_names = list(barracks.keys())
            fuse_dict = {}
            counter = 0
            for n in range(len(b_names)):
                a = barracks[b_names[n]]
                name_checker = a.name
                if name_checker in name_fuse and selection != a:
                    fuse_dict[counter] = b_names[n]
                    counter += 1
            check_fuse = [False, ] * counter
            fuse_setup = False  
        for m in range(counter):
            pick = barracks[fuse_dict[m]]
            logo = Portrait[pick.name]
            columns = 7
            xx = 100 + space * 1.1 * (m % columns)
            yy = 100 * (1 + 1.5 * (m // columns))
            if Button(xx, yy, logo, 1).draw() and not buttoncheck:
                if fuse_counter < 8:
                    buttoncheck = True
                    check_fuse[m] = not check_fuse[m]
                    if not check_fuse[m]:
                        fuse_counter -= 1
                        fuse_list.remove(pick.keyname)
                    else:
                        fuse_list.append(pick.keyname)
                        fuse_counter += 1
                    print(f"Count: {fuse_counter} // {fuse_list}")
            if check_fuse[m]:
                screen.blit(Icon['check'], (xx - 73, yy - 15))
            info = [pick.name, pick.HP, pick.ATK, pick.DEF, pick.WIS, pick.AGI,
                    pick.LV, pick.SEF, pick.rarity]
            cat = ['', 'HP ', 'ATK', 'DEF', 'WIS', 'AGI', 'LV ', 'SEF', '']
            for j in range(len(info)):
                if j == 0:
                    y_text = yy - 10
                    font_a = Fonts['helv20b']
                else:
                    y_text = yy
                    font_a = Fonts['helv10b']
                x_text = xx - 50
                draw_text(f"{cat[j]} {info[j]}", font_a, Colors['white'], x_text, y_text + 18 * j)
        if Button(800, SCREEN_SIZE[1] - 100, Icon['fuse'], 1).draw() and not buttoncheck:
            buttoncheck = True
            if fuse_type == 'self':
                fuse_type = 'sacrifice'
            else:
                fuse_type = 'self'
            fuse_setup = True
        if fuse_counter > 0:
            if Button(500, SCREEN_SIZE[1] - 100, Icon['fuse'], 1).draw() and not buttoncheck:
                fuse_num = fuse_counter
                game_state = 'fuse_animation'
                fuse_timer = 0
                fuse_complete = False

    if game_state == 'fuse_animation':
        fuse_timer += dt
        if fuse_timer >= 1 and not fuse_complete:
            xp = 0
            for n in range(fuse_num):
                xp += barracks[fuse_list[n]].XP
                del barracks[fuse_list[n]]
                xp += 10
            if fuse_num == 8:
                mult_xp = 2
                xp *= 2
            else:
                mult_xp = 1 + (.125 * (fuse_num - 1))
            xp *= mult_xp
            selection.XP += xp
            fuse_complete = True
            print(f"{selection.keyname}: {selection.XP}XP")
        if fuse_timer >= 3:
            game_state = 'band_sort'
            fakeout = True

    if game_state == 'band_setup':
        if RightClick:
            RightClick = False
            game_state = 'main_menu'
        if band_init:
            reserves = barracks
            band_init = False
            for x in range(3):
                for y in range(3):
                    del reserves[band[x][y].keyname]  
        # Display band
        for x in range(3):
            for y in range(3):
                pick = band[x][y]
                pos = [band_pos[x][y][0]/2 - 50, band_pos[x][y][1]/2 - 80]
                hp_tmp = hp_band[x][y]
                screen.blit(Portrait[pick.name], pos)
                if Button(pos[0], pos[1], Portait[pick.name], 1).draw() and not buttoncheck:
                    buttoncheck = True
                    swap_x = x
                    swap_y = y
                draw_text(f"LV {pick.LV}", Fonts['helv15b'], Colors['orange'], pos[0] + 25, pos[1] + 125) 
        rx = band_pos[swap_x][swap_y][0]
        ry = band_pos[swap_x][swap_y][1]
        rectangle = pygame.Rect(rx - 5, ry - 15, space + 5, space + 5)
        pygame.draw.rect(screen, Colors['red'], rectangle, 4)
        # Display barracks
        r_keys = list(reserves.keys())
        r_size = len(r_keys)
        for n in range(r_size):  
            tmp = r_keys[n]
            pick = reserves[tmp]
            logo = Portrait[pick.name]
            columns = 5
            xx = 300 + space * 1.1 * (n % columns)
            yy = 100 * (1 + n // columns)
            if Button(xx, yy, logo, 1).draw():
                selection = pick  
            info = [pick.name, pick.HP, pick.ATK, pick.DEF, pick.WIS, pick.AGI,
                    pick.LV, pick.SEF, pick.rarity]
            cat = ['', 'HP ', 'ATK', 'DEF', 'WIS', 'AGI', 'LV ', 'SEF', '']
            for j in range(len(info)):
                if j == 0:
                    y_text = yy - 10
                    font_a = Fonts['helv20b']
                else:
                    y_text = yy
                    font_a = Fonts['helv10b']
                x_text = xx - 50
                draw_text(f"{cat[j]} {info[j]}", font_a, Colors['white'], x_text, y_text + 18 * j)

    if game_state == 'journey':
        # Draw journey background
        if win_count == num_fights:
            game_state = 'journey_complete'
        elif not encounter:
            journey_timer += dt
            if journey_timer >= (3 / num_fights + random.choice(range(0, 10)) / 10):
                encounter = True
                enemy_power = 0
                og_health = [0, 0, 0]
                enemy_xp = 0
                for x in range(3):
                    pick = open('Uncommon')
                    enemies[x] = Fighter(pick, pick)
                    Portrait[pick] = image(pick)
                    enemies[x].HP = random.choice(range(20, 81))
                    og_health[x] = enemies[x].HP
                    enemies[x].ATK = random.choice(range(1, 6))
                    enemies[x].XP = (enemies[x].HP / 5) + (enemies[x].ATK / 2)
                    enemy_xp += enemies[x].XP
                    enemy_power += enemies[x].ATK
        elif encounter and game_state != 'fight':
            # Draw enemies
            if Button(50, 50, Icon['fight'], 1).draw() and not buttoncheck:
                game_state = 'fight'
                buttoncheck = True

    if game_state == 'journey_complete':
        journey_timer += dt
        if not claimed:
            prize = [0, 0, 0, 0]
            odds = [1, 3, 5, 10]
            for n in range(4):
                prize[n] = random.choice(range(5, 11))
            pixite += prize[0] // odds[0]
            voxite += prize[1] // odds[1]
            doxite += prize[2] // odds[2]
            texite += prize[3] // odds[3]
            claimed = True
        draw_text(f"Journey Complete", Fonts['helv50b'], Colors['white'], 460, 250)
        clr = [Colors['orange'], Colors['white'], Colors['yellow'], Colors['blue']]
        for p in range(4):
            draw_text(f"+{prize[p] // odds[p]}", Fonts['helv40b'], clr[p], 500, 300 + 40 * p)
        if journey_timer >= 3:
            journey_timer = 0
            game_state = 'main_menu'

    if game_state == 'failure':
        fail_time += dt
        draw_text(f"Journey Failed", Fonts['helv50b'], Colors['red'], 460, 250)
        prize = 2
        pixite += prize
        draw_text(f"+{prize}", Fonts['helv40b'], Colors['orange'], 500, 380)
        if fail_time >= 3:
            fail_time = 0
            game_state = 'main_menu'

    if game_state == 'band_sort':
        game_state = 'main_menu'
        overkill = 0
        frontline = [0, 0, 0]
        # Sort by strength
        sort_dict = {}
        xyz = list(barracks.keys())
        for k in range(len(xyz)):
            x_name = xyz[k]
            sort_dict[x_name] = barracks[x_name].ATK
        sort_dict = dict(sorted(sort_dict.items(),
                                        key=lambda item: item[1], reverse=True))
        sorted_names = list(sort_dict.keys())
        lineup = np.array([[3, 1, 4], [5, 0, 6], [7, 2, 8]])
        for x in range(3):
            for y in range(3):
                index = lineup[x][y]
                band[x][y] = barracks[sorted_names[index]] # Automatically assign band of fighter
                hp_band[x][y] = band[x][y].HP

    if game_state == 'fight':
        s = pygame.Surface((540, 545), pygame.SRCALPHA)
        s.fill((25, 25, 25, 100))
        screen.blit(s, (bx, by))
        for x in range(3):
            if enemies[x].HP > 0:
                enemy_hp = enemies[x].HP
                q = len(f"{enemy_hp}")
                villain = Portrait[enemies[x].name]
                villain = pygame.transform.flip(villain, True, False)
                enemy_portrait = colorize(villain, Colors['red'])
                gauge = 100 * enemy_hp / og_health[x]
                rectangle = pygame.Rect(enemies_pos[0][0], 220 + space * x, gauge, 15)
                pygame.draw.rect(screen, Colors['red'], rectangle)
                draw_text(f"{enemy_hp} HP", Fonts['helv10'], Colors['white'],
                          enemies_pos[0][0] + 3, 223 + space * x)
                screen.blit(villain, enemies_pos[x])
                screen.blit(enemy_portrait, enemies_pos[x])
            for y in range(3):
                pick = band[x][y]
                pos = band_pos[x][y]
                hp_tmp = hp_band[x][y]
                if hp_tmp <= 0:
                    band[x][y] = empty
                else:
                    q = len(f"{hp_tmp}")
                    gauge = 100 * hp_tmp / pick.HP
                    rectangle = pygame.Rect(pos[0], pos[1], gauge, 15)
                    pygame.draw.rect(screen, Colors['red'], rectangle)
                    # Draw band with info
                    draw_text(f"{hp_tmp} HP", Fonts['helv10'], Colors['white'],
                              pos[0] + 3, pos[1] + 3)
                    screen.blit(Portrait[pick.name], pos)
                    draw_text(f"LV {pick.LV}", Fonts['helv15b'], Colors['orange'], pos[0] + 25, pos[1] + 125)
                    draw_text(f"{pick.ATK} ATK", Fonts['helv15b'], Colors['red'], pos[0] + 90, pos[1] + 125)

        total_health = np.array([0, 0, 0])
        for n in range(3):
            total_health[n] = enemies[n].HP

        if np.sum(total_health) == 0 and not victory:
            victory = True
            enemy_power = 0
            victory_time = 0

        if np.sum(hp_band) <= 0:
            death_time += dt
            if death_time > 3:
                game_state = 'failure'
                enemy_power = 0
                fail_time = 0
                death_time = 0
                encounter = False
                journey_timer = 0

        if victory:
            victory_time += dt
            if victory_time >= 3:
                for x in range(3):
                    for y in range(3):
                        band[x][y].XP += enemy_xp
                win_count += 1
                encounter = False 
                game_state = 'journey'
                victory = False
                victory_time = 0
                journey_timer = 0
                claimed = False

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
            attack_timer = 0
            queue += 1
            if queue == 3:
                attack_state = True

        if attack_state:    # Attack animations
            attack_timer += dt
            power = 0
            t1 = 0.6
            t2 = 0.82
            t3 = 1.6
            speed = 1300
            if attack_counter < 3:
                if t1 < attack_timer <= t2:
                    xx = front_pos[0] + (attack_timer-t1) * speed
                elif t2 < attack_timer <= t3:
                    strike = True
                    xx = front_pos[0] + (t2 - t1) * speed - (attack_timer-t2) * 400
                    for j in range(3):
                        draw_text(f"-{damage[j]}", Fonts['helv30b'], dmg_color[j], enemies_pos[0][0] - 20, enemies_pos[0][1] + space * j)
                    if xx < front_pos[0]:
                        xx = front_pos[0]
                for y in range(3):
                    k = attack_counter
                    screen.blit(Portrait[attack_order[k][y].name], (xx, front_pos[1] + space * y))
                    power += attack_order[k][y].ATK
                else:
                    xx = front_pos[0]
            if strike and not strike_hold:
                dmg_color = [Colors['orange'],] * 3
                for j in range(3):
                    modifier = 1
                    crit_chance = 100
                    if 1 == random.choice(range(crit_chance)):
                        dmg_color[j] = Colors['red']
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
                if victory:
                    attack_counter = 3
                attack_timer = 0
                strike_hold = False
                strike = False
            if attack_counter == 3:
                enemy_attack = True
                attack_state = False

        if enemy_attack:
            attack_timer += dt
            enemy_power = 0
            for x in range(3):
                if enemies[x].HP > 0:
                    enemy_power += enemies[x].ATK
            if attack_timer > 0.5 and not enemy_done:
                hp_band -= enemy_power
                if np.sum(hp_band) <= 0:
                    death_time = 0
                enemy_done = True
            elif enemy_done:
                draw_text(f"-{enemy_power}", Fonts['helv35b'], Colors['orange'], 300, 100)
                if attack_timer > 2:
                    queue = 0
                    enemy_attack = False
                    enemy_done = False
                    attack_counter = 0
                    attack_timer = 0
                    attack_order = {}
                    swipe_order = [0,]
                    strike_hold = False
                    strike = False

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
