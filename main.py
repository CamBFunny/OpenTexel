import pygame
import data
import time
import numpy as np
import os
import random
import inspect
import asyncio
import math
# Import buttons
from pygame.locals import (KEYDOWN, QUIT, KEYUP, K_LCTRL,
    K_UP, K_DOWN, K_LEFT, K_RIGHT, K_ESCAPE, K_TAB, K_LSHIFT, K_SPACE,
    K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9, K_0,
                           K_q, K_w, K_e, K_r, K_t,
                           K_a, K_s, K_d, K_f, K_g,
                           K_z, K_x, K_c, K_v, K_b)

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
barracks = {}

running = True
keys_pressed = set()
clock = pygame.time.Clock()
framerate = 60; dt = 0      # Makes time-based calculations relative to framerate
# pygame.mouse.set_visible(False)     # Hide mouse cursor

# Screen settings
resolution = 1             # Set window size; 16:9 ratio .8-720p .6-540p .5~480p
SCREEN_SIZE = [int(1440 * resolution), int(900 * resolution)]
screen = pygame.display.set_mode([SCREEN_SIZE[0], SCREEN_SIZE[1]])
# Initialize PyGame
pygame.init()
pause = False
true_counter = 0
realtime = 0
frame_counter = 0
mouse_pos = pygame.mouse.get_pos()

Fonts = {}
fsizes = [10, 15, 20, 23, 25, 30, 37, 40, 55]

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

# // FUNCTIONS //
def draw_text(text, font, text_col, x, y):  # Function for outputting text onto the screen
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

Portrait = {}

def image(name):
    name = pygame.image.load(f"lib/fighters/{name}_Sprite.webp")
    return name

background = pygame.image.load(f"lib/images/background.png")
sz = background.get_size()
scl = SCREEN_SIZE[0] / sz[0]
background = pygame.transform.scale(background, (sz[0] * scl, sz[1] * scl))

def open(box):
    if box == 'Basic':
        value = random.choice(roster)

    return value

fighters = os.listdir('lib/fighters/')
num_fighters = len(fighters)
roster = {}
for n in range(num_fighters):
    sz = len(fighters[n])
    for m in range(sz):
        if fighters[n][m] == '_':
            end = m
    roster[n] = fighters[n][0:end]

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

LeftHold = False
LeftClick = False
fight = False

while running: 
    # CONTROLS
    for event in pygame.event.get():
        # Reading Keyboard Input
        if event.type == KEYDOWN:
            keys_pressed.add(event.key)  
        if event.type == pygame.QUIT:
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


    if len(list(barracks.keys())) < 9:
        pick = open('Basic')
        before = pick
        while pick in barracks.keys():
            p = 1
            pick = f"{pick}-{p}"
            p += 1
        barracks[pick] = Fighter(before)
        Portrait[before] = image(before)
    elif not fight:
        fight = True
        # Temporary band setup, remove once menus work
        xyz = list(barracks)
        for x in range(3):
            for y in range(3):
                index = x * 3 + y
                band[x][y] = barracks[xyz[index]] # Automatically assign band fighter

    # Source - https://stackoverflow.com/a/6350227
    # Posted by Gustavo Giráldez
    # Retrieved 2026-03-06, License - CC BY-SA 3.0

    s = pygame.Surface((520, 515), pygame.SRCALPHA)  # per-pixel alpha
    s.fill((25, 25, 25, 80))  # notice the alpha value in the color
    screen.blit(s, (170, 300))

    if fight:
        for x in range(3):
            for y in range(3):
                pick = band[x][y]
                space = 150
                xx = 200 + space*x
                yy = 330 + space*y
                screen.blit(Portrait[pick.name], (xx, yy))
                draw_text(f"LV {pick.LV}", Fonts['helv15b'], Colors['orange'], xx + 20, yy + 125)

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
