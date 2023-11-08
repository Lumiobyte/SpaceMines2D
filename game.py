# Notes
# A random point in the mining zone should be picked as a resource "hotspot" - the production of each mine is a measure of how close / far the mine is from this point
# The player can choose where to place mines within the mine field, and they can learn where the hotspot is over time through trial and error

# Buttons can use the animation system to have a click effect - just call next_frame() when they are clicked and again when the click is released.
# Should have a cool civ-style "NEXT YEAR" button in the bottom right corner

import pygame
from pygame.locals import *

import ctypes
import sys
import random
import math
import os

# Initialise
ctypes.windll.user32.SetProcessDPIAware()
pygame.init()

# Import custom modules
from classes import *
from text import Text

###############
##### Functions

def setup():
    # Native resolution is 2560 x 1440 fullscreen (16:9)

    display_info = pygame.display.Info()
    print(display_info)

    if True: # If Fullscreen
        if math.isclose((display_info.current_w / display_info.current_h), 1.77, abs_tol = 10**-3): # If the screen is 16:9
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else: # Otherwise, render a 16:9 game with black bars on the top and bottom to prevent warping of the game
            fullscreen_res = (display_info.current_w, round(display_info.current_w / 1.77778)) # Potentially round the y value up
            screen = pygame.display.set_mode(fullscreen_res, pygame.FULLSCREEN|pygame.SCALED)
    else:
        screen = pygame.display.set_mode((800, 450))

    return screen

###############
##### Variables

screen = setup()
clock = pygame.time.Clock()
frame_time = 0

print(screen.get_width())
print(screen.get_height())

game_res = GameResolution((2560, 1440), (screen.get_width(), screen.get_height()), Point(screen.get_width() / 2560, screen.get_height() / 1440))

print(game_res.scaling_factor.x)
print(game_res.scaling_factor.y)

text = Text(game_res.scaling_factor.y)

smile = Image("images/smile.png", game_res)
diamond = AnimatedImage("images/diamond", 100, game_res)

###############
##### Main Loop

while True:

    ### Events

    for event in pygame.event.get():

        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()

        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    ### Logic

    diamond.tick(frame_time)

    ### Render

    screen.fill(Colours.RED)

    text.write(screen, text.MED_BOLD, Colours.BLUE, (10, 10), f"FPS: {round(clock.get_fps(), 1)}")

    smile.render(screen, Point(300, 300))
    diamond.render(screen, Point(800, 300))

    pygame.display.flip()
    frame_time = clock.tick(60)