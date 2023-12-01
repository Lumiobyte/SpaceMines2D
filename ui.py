import enum
import pygame
from classes import *

def map_mouse_position(pos, game_res: GameResolution):
    """ This function maps the real mouse position on the screen to its relative position on the unscaled game window. 
        Due to the way the alternate resolution settings are implemeneted, without this mouse mapping, buttons would be
        difficult or impossible to press and the visual position of the cursor on the screen would be different to where the game thinks it is. """

    if game_res.scaling_factor.x != 1: # If there is any need to scale
        x_map = ((game_res.native_res[0]) / (game_res.current_res[0]) * (pos[0]))
        y_map = ((game_res.native_res[1]) / (game_res.current_res[1]) * (pos[1]))

    return (x_map, y_map)

class Text:
    def __init__(self, scaling_factor):
        self.TINY = pygame.font.Font("fonts/segoe/segoe-ui.ttf", int(16 * scaling_factor))
        self.SMALL = pygame.font.Font("fonts/segoe/segoe-ui.ttf", int(24 * scaling_factor))
        self.SMALL_BOLD = pygame.font.Font("fonts/segoe/segoe-ui-bold.ttf", int(24 * scaling_factor))
        self.MEDIUM = pygame.font.Font("fonts/segoe/segoe-ui.ttf", int(32 * scaling_factor))
        self.LARGE = pygame.font.Font("fonts/segoe/segoe-ui.ttf", int(48 * scaling_factor))
        self.MED_BOLD = pygame.font.Font("fonts/segoe/segoe-ui-bold.ttf", int(48 * scaling_factor))
        self.LARGE_BOLD = pygame.font.Font("fonts/segoe/segoe-ui-bold.ttf", int(64 * scaling_factor))

    def write(self, screen, font, colour, location, text, centered = False):

        if centered:
            text_render = font.render(text, True, colour)
            screen.blit(text_render, text_render.get_rect(center = location))
        else:
            screen.blit(font.render(text, True, colour), location)

class ButtonType(enum.Enum):
    NORMAL = enum.auto()
    CHECKBOX = enum.auto()

class Button:
    def __init__(self, type: ButtonType, pos: Point, size: Point, title: str, colours: list[Colours], images: list | None, actions: list):


        self.type = type
        self.pos = pos # x, y of center
        self.size = size # width, height
        self.title = title # Should be a rendered text obj
        self.colours = colours # [Default BG, Hovered BG]
        self.images = images # [Default IMG, Hovered IMG] or None if not used
        self.actions = actions # List of functions

        self.hovered = False

        self.button_rect = pygame.Rect((self.pos.x - self.size.x / 2), (self.pos.y - self.size.y / 2), self.size.x, self.size.y)

    def check(self, mouse_pos: tuple, clicked):

        if self.images:
            current_image = self.images[{True: 1, False: 0}[self.hovered]]
            collide_rect = pygame.Rect((self.pos.x - current_image.get_rect().width / 2), (self.pos.y - current_image.get_rect().height / 2), current_image.get_rect().width, current_image.get_rect().height)
        else:
            collide_rect = self.button_rect

        if collide_rect.collidepoint(mouse_pos):
            self.hovered = True

            if clicked:
                for i, action in enumerate(self.actions):
                    if self.type == ButtonType.CHECKBOX and i == 0: # Checkbox specific logic
                        result = action()
                        if result:
                            #self.title = TextSize.SMALL_BOLD.render("X", True, Colours.BLACK) # Always using smallbold, does not account for varying button sizes
                            # Need to add another checked indicator
                            pass
                        else:
                            self.title = None
                    else: # Default button type logic
                        action()
                        return True

    def render(self, screen, delta):

        if self.images:
            if isinstance(self.images[{True: 1, False: 0}[self.hovered]], AnimatedImage):
                self.images[{True: 1, False: 0}[self.hovered]].tick(delta)
            self.images[{True: 1, False: 0}[self.hovered]].render(screen, self.pos, True)
        else:
            pygame.draw.rect(screen, self.colours[0] if not self.hovered else self.colours[1], self.button_rect)

        if self.type == ButtonType.CHECKBOX: 
            # Probably very expensive and has performance impact but.. oh well! 
            # Interior colour also does not account for the main colour being totally black
            top_offset = self.size.y / 8
            left_offset = self.size.x / 8
            interior_rect = pygame.Rect(self.button_rect.left + left_offset, self.button_rect.top + top_offset, self.size.x - left_offset * 2, self.size.y - top_offset * 2)
            pygame.draw.rect(screen, self.__darken_colour(self.colours[0]) if not self.hovered else self.__darken_colour(self.colours[1]), interior_rect)

        if self.title:
            screen.blit(self.title, self.title.get_rect(center = (self.pos.x, self.pos.y)))

        self.hovered = False

    def __darken_colour(self, colour):
        return (colour[0] - 40, colour[1] - 40, colour[2] - 40)

class ZoomAnimation: # Should support different zooms e.g. linear, lerp, ease in/out via either lambda functions or some setting variable. Also support reversing
    def __init__(self, frames: int, frame_length: float):

        self.frames = frames
        self.frame_length = frame_length

        self.scale_per_frame = 1 / frames

        self.current_frame = 0
        self.time_until_next = self.frame_length

        self.playing = False

    def play(self, size: Point, delta):
        if not self.playing:
            self.playing = True
            self.current_frame = 0

        self.time_until_next -= delta

        if self.time_until_next <= 0:
            if self.current_frame < self.frames:
                self.current_frame += 1
            elif self.current_frame >= self.frames:
                self.playing = False

        scale_fact = self.scale_per_frame * self.current_frame
        return size * scale_fact
            

class InfoBox:
    def __init__(self, size: Point, pos: Point, game_res: GameResolution, data: dict, animation: ZoomAnimation):

        self.game_res = game_res

        self.size = size
        self.scaled_size = self.size * self.game_res.scaling_factor

        self.pos = pos * self.game_res.scaling_factor # Will probably just be screen center most of the time

        self.data = data
        # Data format
        # "colour": colour of the infobox
        # "text": list containing tuples of (text object, Point coordinates, centered boolean)
        # "images": list containing tuples of (Image or AnimatedImage object, Point coordinates)
        # "shapes": list containing rects, spheres, etc
        # "startup_functions": functions only run in open()
        # "functions": references to functions which can be called by this infobox
        # "funcdata": a list of any data needed to be referenced by those functions
        # "buttons": a list of Button objects which can be iterated through to run .process() and .render() on each

        self.animation = animation

        self.newly_opened = True # Tells the infobox that it just switched from closed to open state

        self.mouse_pos = Point(1280, 720)


    def adjust_cursor(self, mouse_pos):
        return Point(mouse_pos.x - ((self.game_res.current_res[0] / 2) - (self.scaled_size.x / 2)), mouse_pos.y - ((self.game_res.current_res[1] / 2) - (self.scaled_size.y / 2)))

    def blit_text(self, dest, text, location, centered = False):
        if centered:
            dest.blit(text, text.get_rect(center = location))
        else:
            dest.blit(text, location)

    def redefine_data(self, data_type, new_data):
        self.data[data_type] = new_data

    def open(self, delta):

        self.newly_opened = True # This is later set to false in main function, after the dimming overlay is rendered
        self.animation.play(self.size, delta)

    def process(self, mouse_pos: Point, clicks, keys):

        if self.animation and self.animation.playing: # Wait until animation is finished before accepting inputs
            return

        # Process all inputs
        self.mouse_pos = self.adjust_cursor(mouse_pos) * (self.size.x / self.scaled_size.x)

        data_buttons = self.data.get("buttons")
        if data_buttons:
            for btn in data_buttons:
                btn.check(self.mouse_pos.tuple(), clicks[0])


    def render(self, screen, delta):

        infobox_surface = pygame.Surface((self.size.x, self.size.y))

        final_size = self.scaled_size
        if self.animation and self.animation.playing:
            final_size = self.animation.play(self.scaled_size, delta)

        # Rendering
        infobox_surface.fill(Colours.BLACK)
        offset = 5 * self.game_res.scaling_factor.x
        pygame.draw.rect(infobox_surface, Colours.INFOBOX_BORDER, pygame.Rect(offset, offset, self.size.x - offset * 2, self.size.y - offset * 2))
        pygame.draw.rect(infobox_surface, self.data["colour"], pygame.Rect(offset * 2, offset * 2, self.size.x - offset * 4, self.size.y - offset * 4))

        data_buttons = self.data.get("buttons")
        if data_buttons:
            for btn in data_buttons:
                btn.render(infobox_surface, delta)

        data_text = self.data.get("text")
        if data_text:
            for item in data_text:
                self.blit_text(infobox_surface, item[0], item[1].tuple(), item[2])

        # Scale and blit surface
        infobox_surface = pygame.transform.scale(infobox_surface, final_size.tuple())

        blit_pos = (self.pos.x - (infobox_surface.get_width() / 2), self.pos.y - (infobox_surface.get_height() / 2))
        screen.blit(infobox_surface, blit_pos)

        return pygame.Rect(*blit_pos, self.scaled_size.x, self.scaled_size.y)
    
class SatisfactionDial:
    def __init__(self, screen, game_res, satisfaction):

        self.screen = screen
        self.scaling_factor = game_res.scaling_factor

        self.dial = Image("images/dial.png", game_res).return_scaled_image()
        self.hand = Image("images/dialhand.png", game_res).return_scaled_image()

        self.rotated_rect = None
        self.rotated_hand = None
        self.rotate_hand(satisfaction)

    def rotate_hand(self, satisfaction):
        hand_angle = -(-90 + ((satisfaction - 0.6) / (1.2 - 0.6) * (90 - (-90))))

        self.rotated_hand = pygame.transform.rotozoom(self.hand, hand_angle, 1)

        pivot_point = (self.dial.get_width() / 2, self.dial.get_height() - (1 * self.scaling_factor.y))
        offset = pygame.math.Vector2(pivot_point).rotate(hand_angle)

        self.rotated_rect = self.rotated_hand.get_rect(center = pivot_point + offset)

    def render(self, pos: Point):
        pos = pos * self.scaling_factor
        self.screen.blit(self.dial, (pos.x + self.dial.get_width() / 2, pos.y + self.dial.get_height() - (80 * self.scaling_factor.y)))

        self.rotated_rect.top = pos.y + self.dial.get_height() - self.hand.get_height() + (4 * self.scaling_factor.y)
        self.rotated_rect.left = pos.x + self.dial.get_width() - self.hand.get_width() / 2 - (2 * self.scaling_factor.x)

        self.screen.blit(self.rotated_hand, self.rotated_rect)

        #pygame.draw.rect(self.screen, Colours.WHITE, self.rotated_rect)
