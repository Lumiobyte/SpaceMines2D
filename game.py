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
import ui

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
        screen = pygame.display.set_mode((1200, 675))

    return screen

def scale_rect(rect: pygame.Rect, game_res):
    return pygame.Rect(rect.left * game_res.scaling_factor.x, rect.top * game_res.scaling_factor.y, rect.width * game_res.scaling_factor.x, rect.height * game_res.scaling_factor.y)

###############
##### Variables

screen = setup()
clock = pygame.time.Clock()
frame_time = 0
game_res = GameResolution((2560, 1440), (screen.get_width(), screen.get_height()), Point(screen.get_width() / 2560, screen.get_height() / 1440))
text = ui.Text(game_res.scaling_factor.y)

# Controls which screen is currently being displayed
# 0 = Main Menu / 1 = Game
view = 1

update_zones = []

background_rects = [scale_rect(pygame.Rect(350, 100, 800, 800), game_res), scale_rect(pygame.Rect(1410, 100, 800, 800), game_res)]

current_infobox = -1
infoboxes = [
    ui.InfoBox(Point(300, 300) * game_res.scaling_factor, Point(1280, 720) * game_res.scaling_factor, {}, ui.ZoomAnimation(8, 0.05))
]

miner = AnimatedImage("images/miners", 1000, game_res)
house = AnimatedImage("images/houses", 1200, game_res)

###############
##### Main Loop

while True:

    ### Events

    for event in pygame.event.get():

        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()

            if event.key == K_o:

                if current_infobox == 0 and not infoboxes[0].animation.playing:
                    current_infobox = -1
                elif current_infobox == -1:
                    current_infobox = 0
                    infoboxes[0].open(frame_time)

        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    if view == 0: # MAIN MENU
        pass

    elif view == 1: # GAME

        ##### UI Logic #####

        if current_infobox > -1:
            infoboxes[current_infobox].process(None, None, None)
            update_zones.append(infoboxes[current_infobox].render(screen, frame_time))

        ##### Logic #####

        miner.tick(frame_time)
        house.tick(frame_time)

        ##### Render #####
        
        if current_infobox < 0:

            # Background
            screen.fill(Colours.BLUE)
            
            pygame.draw.rect(screen, Colours.LIGHT_GRAYBLUE, background_rects[0])
            pygame.draw.rect(screen, Colours.LIGHT_BLUE, background_rects[1])

            # Images + Animations

            miner.render(screen, Point(400, 400))
            house.render(screen, Point(1600, 400))

            # Text
            text.write(screen, text.SMALL, Colours.BLACK, (10, 1400), f"FPS: {round(clock.get_fps(), 1)}")


        elif infoboxes[current_infobox].newly_opened: # When infobox was just opened

            background_dimmer = pygame.Surface((screen.get_width(), screen.get_height()))
            background_dimmer.set_alpha(100)
            background_dimmer.fill(Colours.BLACK)

            screen.blit(background_dimmer, (0, 0))


    if len(update_zones) > 0:
        if infoboxes[current_infobox].newly_opened: # Do one full pass to ensure that the dimming surface is rendered
            pygame.display.flip()
            infoboxes[current_infobox].newly_opened = False

        else: # Only update the pixels containing infoboxes
            for zone in update_zones:
                pygame.display.update(zone)

            update_zones = []
    else:
        pygame.display.flip()

    frame_time = clock.tick(60)