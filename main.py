import pygame
import data
import time
import numpy as np
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

def Fighter(self, name, HP, ATK, DEF, WIS, AGI, LV, SEF, rarity, tribe, sign, type)
    Fighter.name = name
    Fighter.HP = HP
    Fighter.ATK = ATK
    Fighter.DEF = DEF
    Fighter.WIS = WIS
    Fighter.AGI = AGI
    Fighter.LV = LV
    Fighter.SEF = SEF
    Fighter.rarity = rarity
    Fighter.tribe = tribe
    Fighter.sign = sign
    Fighter.type = type

empty = Fighter('-', 0, 0, 0, 0, 0, 0, 0, 'null', 'null', 'null', 'null')
band = np.array([['empty',] * 3]*3)
running = True
keys_pressed = set()
clock = pygame.time.Clock()
framerate = 60; dt = 0      # Makes time-based calculations relative to framerate
# pygame.mouse.set_visible(False)     # Hide mouse cursor

# Screen settings
resolution = .96             # Set window size; 16:9 ratio .8-720p .6-540p .5~480p
SCREEN_SIZE = [int(1600 * resolution), int(900 * resolution)]
screen = pygame.display.set_mode([SCREEN_SIZE[0], SCREEN_SIZE[1]])
# Initialize PyGame
pygame.init()

# // FUNCTIONS //
def draw_text(text, font, text_col, x, y):  # Function for outputting text onto the screen
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

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

while running: 
    # CONTROLS
    for event in pygame.event.get():
        # Reading Keyboard Input
        if event.type == KEYDOWN:
            keys_pressed.add(event.key)  
        if event.type == pygame.QUIT:
            true_pause = True
        # Reading Mouse Input
        if event.type == pygame.MOUSEWHEEL:
            if event.y == 1:
                wheel_up = True
            if event.y == -1:
                wheel_down = True
        if pygame.mouse.get_pressed()[0] and not LeftClick and not LeftHold:	    # Left Click
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
