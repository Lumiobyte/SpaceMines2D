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
from dataclasses import dataclass

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

    # This function simply creates the game window, and applies adjustments if the screen aspect ratio is not 16:9, or if the game is running in windowed mode. 

    display_info = pygame.display.Info()

    if False: # If Fullscreen
        if math.isclose((display_info.current_w / display_info.current_h), 1.77, abs_tol = 10**-3): # If the screen is 16:9
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else: # Otherwise, render a 16:9 game with black bars on the top and bottom to prevent warping of the game
            fullscreen_res = (display_info.current_w, round(display_info.current_w / 1.77778)) # Potentially round the y value up
            screen = pygame.display.set_mode(fullscreen_res, pygame.FULLSCREEN|pygame.SCALED)
    else:
        screen = pygame.display.set_mode((2560, 1440))

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

@dataclass
class GameData:
    year = random.randint(2300, 2501)

    mines = random.randint(3, 8)
    people = random.randint(40, 80)
    money = random.randint(200, 500) * people

    food_price = random.randint(100, 300)
    ore_price = random.randint(50, 80)
    mine_price = random.randint(3000, 6000)

    ore_per_mine = random.randint(8, 20)

    stored_food = 100
    stored_ore = random.randrange(40, 80)
    satisfaction = 1

    food_price_change = 0
    ore_price_change = 0
    mine_price_change = 0
    ore_produced = 0

satisfaction_dial = ui.SatisfactionDial(screen, game_res, GameData.satisfaction)

###############
##### Functions

def close_infobox():
    global current_infobox
    current_infobox = -1

def next_year():
    global current_infobox
    global infoboxes
    global frame_time

    GameData.year += 1

    GameData.mine_price_change = (random.randint(55 if GameData.mine_price > 800 else 120, 145) / 100)
    GameData.mine_price = int(GameData.mine_price * GameData.mine_price_change)

    GameData.ore_price_change = (random.randint(75 if GameData.ore_price > 40 else 115, 125) / 100) 
    GameData.ore_price = int(GameData.ore_price * GameData.ore_price_change)

    GameData.food_price_change = (random.randint(80 if GameData.food_price > 40 else 110, 120) / 100) 
    GameData.food_price = int(GameData.food_price * GameData.food_price_change)

    GameData.ore_produced = GameData.ore_per_mine * (GameData.mines - random.randint(0, 1))
    GameData.stored_ore += GameData.ore_produced

    current_infobox = 0
    infoboxes[current_infobox].open(frame_time)

def sell_ore():
    GameData.money += GameData.stored_ore * GameData.ore_price
    GameData.stored_ore = 0

def buy_mine():
    if GameData.money > GameData.mine_price and GameData.mines < 16:
        GameData.money -= GameData.mine_price
        GameData.mines += 1

def sell_mine():
    if GameData.mines > 0:
        GameData.mines -= 1
        GameData.money += GameData.mine_price

def buy_food():
    if GameData.money > GameData.food_price * 10:
        GameData.stored_food += 10
        GameData.money -= GameData.food_price * 10

###############
##### GUI/Asset

background_rects = [scale_rect(pygame.Rect(350, 100, 800, 800), game_res), scale_rect(pygame.Rect(1410, 100, 800, 800), game_res), scale_rect(pygame.Rect(0, 1000, 2560, 440), game_res)]

current_infobox = -1
infoboxes = [
    ui.InfoBox(Point(1200, 900), Point(1280, 720), game_res, {
        "colour": Colours.INFOBOX_GREY,
        "text": [], # this is set in update_yearly_report as these values need to be changed each year
        "buttons": [ui.Button(ui.ButtonType.NORMAL, Point(600, 830), Point(160, 90), text.MED_BOLD.render("OK", True, Colours.BLACK), [Colours.BUTTON, Colours.BUTTON_HOVER], None, [close_infobox])]
    }, ui.ZoomAnimation(8, 0.05)),
    ui.InfoBox(Point(800, 600), Point(1280, 720), game_res, {"colour": Colours.INFOBOX_GREY, "text": [(text.LARGE_BOLD.render("YOU LOST", True, Colours.WHITE), Point(600, 70), True)], "buttons": [ui.Button(ui.ButtonType.NORMAL, Point(400, 520), Point(120, 80), text.MED_BOLD.render("OK", True, Colours.BLACK), [Colours.BUTTON, Colours.BUTTON_HOVER], None, [close_infobox])]}, ui.ZoomAnimation(8, 0.05))
]

##############
##### Infobox Helpers

def update_yearly_report():
    global infoboxes
    
    """
    infoboxes[0].redefine_data("text", [
        (text.LARGE_BOLD.render("THE YEARS MARCH ON", True, Colours.WHITE), Point(600, 70), True),
        (text.SMALL_BOLD.render(f"It is now {GameData.year}", True, Colours.TEXT_SUBTITLE), Point(600, 120), True),
        (text.MED_BOLD.render("Economic Report", True, Colours.TEXT_LIGHT), Point(300, 270), True),
        (text.MED_BOLD.render("Colony Status", True, Colours.TEXT_LIGHT), Point(900, 270), True),

        (text.SMALL_BOLD.render(f"Ore Price: {GameData.ore_price} | {'+' if GameData.ore_price_change >= 0 else ''}{GameData.ore_price_change}%", True, Colours.TEXT_LIGHT), Point(180, 350), False),
        (text.SMALL_BOLD.render(f"Mine Price: {GameData.mine_price} | {'+' if GameData.mine_price_change >= 0 else ''}{GameData.mine_price_change}%", True, Colours.TEXT_LIGHT), Point(180, 400), False),
        (text.SMALL_BOLD.render(f"Food Price: {GameData.food_price} | {'+' if GameData.food_price_change >= 0 else ''}{GameData.food_price_change}%", True, Colours.TEXT_LIGHT), Point(180, 450), False),

    ])
    """
    
    infoboxes[0].redefine_data("text", [
        (text.LARGE_BOLD.render("THE YEARS MARCH ON", True, Colours.WHITE), Point(600, 70), True),
        (text.SMALL_BOLD.render(f"It is now {GameData.year}", True, Colours.TEXT_SUBTITLE), Point(600, 120), True),
    ])
    

    pass


update_yearly_report() # Run it for the first time, so that the infobox is set up with the initial values

##### Infobox Helpers
##############

buttons = [
    ui.Button(ui.ButtonType.NORMAL, Point(2400, 1180), Point(160, 90), None, [Colours.BUTTON, Colours.BUTTON_HOVER], [Image("images/calendar.png", game_res), AnimatedImage("images/acalendar", 100, game_res)], [next_year, update_yearly_report]),
    
    ui.Button(ui.ButtonType.NORMAL, Point(200, 1300), Point(160, 70), text.SMALL_BOLD.render("Sell Ore", True, Colours.BLACK), [Colours.BUTTON, Colours.BUTTON_HOVER], None, [sell_ore]),
    ui.Button(ui.ButtonType.NORMAL, Point(620, 1350), Point(90, 60), text.MED_BOLD.render("-", True, Colours.BLACK), [Colours.BUTTON, Colours.BUTTON_HOVER], None, [sell_mine]),
    ui.Button(ui.ButtonType.NORMAL, Point(780, 1350), Point(90, 60), text.MED_BOLD.render("+", True, Colours.BLACK), [Colours.BUTTON, Colours.BUTTON_HOVER], None, [buy_mine]),
    ui.Button(ui.ButtonType.NORMAL, Point(1300, 1350), Point(160, 70), text.SMALL_BOLD.render("Buy Food", True, Colours.BLACK), [Colours.BUTTON, Colours.BUTTON_HOVER], None, [buy_food])
]

miner = AnimatedImage("images/miners", 1000, game_res)
house = AnimatedImage("images/houses", 1200, game_res)

ore_icon = Image("images/ore.png", game_res)
dollar_icon = Image("images/dollar.png", game_res)
mines_icon = Image("images/mines.png", game_res)
food_icon = Image("images/food.png", game_res)
people_icon = Image("images/people.png", game_res)

miner_positions = [
Point(320, 50) * game_res.scaling_factor,
Point(320, 240) * game_res.scaling_factor,
Point(320, 430) * game_res.scaling_factor,
Point(320, 620) * game_res.scaling_factor,
Point(520, 50) * game_res.scaling_factor,
Point(520, 240) * game_res.scaling_factor,
Point(520, 430) * game_res.scaling_factor,
Point(520, 620) * game_res.scaling_factor,
Point(720, 50) * game_res.scaling_factor,
Point(720, 240) * game_res.scaling_factor,
Point(720, 430) * game_res.scaling_factor,
Point(720, 620) * game_res.scaling_factor,
Point(920, 50) * game_res.scaling_factor,
Point(920, 240) * game_res.scaling_factor,
Point(920, 430) * game_res.scaling_factor,
Point(920, 620) * game_res.scaling_factor,
]

house_positions = []
for position in miner_positions:
    house_positions.append(position + Point(1075, 35) * game_res.scaling_factor)

###############
##### Main Loop

while True:

    ### Events

    pressed_keys = []
    pressed_clicks = [False, False, False]

    for event in pygame.event.get():

        if event.type == MOUSEBUTTONDOWN:
            pressed_clicks = pygame.mouse.get_pressed()

        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()

        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    if view == 0: # MAIN MENU
        pass

    elif view == 1: # GAME

        ##### UI Logic #####

        # Infoboxes
        if current_infobox > -1:
            infoboxes[current_infobox].process(Point(*pygame.mouse.get_pos()), pressed_clicks, None)
            update_zones.append(infoboxes[current_infobox].render(screen, frame_time))
        else:
        # Check buttons outside of infoboxes
            for button in buttons:
                button.check(pygame.mouse.get_pos(), pressed_clicks[0])

        ##### Logic #####

        miner.tick(frame_time)
        house.tick(frame_time)

        ##### Render #####
        
        if current_infobox < 0:

            # Background
            screen.fill(Colours.BLUE)
            
            pygame.draw.rect(screen, Colours.LIGHT_GRAYBLUE, background_rects[0])
            pygame.draw.rect(screen, Colours.LIGHT_BLUE, background_rects[1])
            pygame.draw.rect(screen, Colours.PANEL_DARKGREY, background_rects[2])

            # Gameplay Images + Animations
            for position in miner_positions[0:GameData.mines]:
                miner.render(screen, position)

            houses = int(GameData.people / 8)
            if houses > 16:
                houses = 16
            for position in house_positions[0:houses]:
                house.render(screen, position)

            # Buttons
            for button in buttons:
                button.render(screen, frame_time)

            # Rendering hotbar elements
            text.write(screen, text.MEDIUM, Colours.TEXT_SUBTITLE, (2300, 1330), "Next Year")
            text.write(screen, text.LARGE_BOLD, Colours.TEXT_LIGHT, (200, 1050), "ORE", True)
            

            ore_icon.render(screen, Point(130, 1120), True)
            dollar_icon.render(screen, Point(130, 1190), True)
            text.write(screen, text.SMALL, Colours.TEXT_SUBTITLE, (165, 1100), f"Stored: {GameData.stored_ore}T")
            text.write(screen, text.SMALL, Colours.TEXT_SUBTITLE, (165, 1170), f"Price: ${GameData.ore_price}")

            text.write(screen, text.LARGE_BOLD, Colours.TEXT_LIGHT, (700, 1050), "MINES", True)

            ore_icon.render(screen, Point(630, 1120), True)
            dollar_icon.render(screen, Point(630, 1190), True)
            mines_icon.render(screen, Point(630, 1270), True)

            text.write(screen, text.SMALL, Colours.TEXT_SUBTITLE, (665, 1100), f"{GameData.ore_per_mine}T/mine")
            text.write(screen, text.SMALL, Colours.TEXT_SUBTITLE, (665, 1170), f"Price: ${GameData.mine_price}")
            text.write(screen, text.MEDIUM, Colours.WHITE, (665, 1250), f"Mines: {GameData.mines}")


            text.write(screen, text.LARGE_BOLD, Colours.TEXT_LIGHT, (1300, 1050), "FOOD", True)

            food_icon.render(screen, Point(1230, 1120), True)
            dollar_icon.render(screen, Point(1230, 1190), True)

            text.write(screen, text.SMALL, Colours.TEXT_SUBTITLE, (1265, 1100), f"Food: {GameData.stored_food} units")
            text.write(screen, text.SMALL, Colours.TEXT_SUBTITLE, (1265, 1170), f"Price: ${GameData.food_price}")


            text.write(screen, text.LARGE_BOLD, Colours.TEXT_LIGHT, (1900, 1050), "COLONY", True)

            people_icon.render(screen, Point(1830, 1120), True)
            dollar_icon.render(screen, Point(1830, 1190), True)
            text.write(screen, text.SMALL, Colours.TEXT_SUBTITLE, (1865, 1100), f"{GameData.people} residents")
            text.write(screen, text.SMALL, Colours.TEXT_SUBTITLE, (1865, 1170), f"Bank: ${GameData.money}")


            #text.write(screen, text.SMALL, Colours.BLACK, (10, 1400), f"FPS: {round(clock.get_fps(), 1)}")


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
        #pygame.draw.circle(screen, Colours.RED, pygame.mouse.get_pos(), 3)
        pygame.display.flip()

    frame_time = clock.tick(60)