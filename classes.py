import pygame
from dataclasses import dataclass
import math
import glob

class Colours:
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    FULLBLUE = (0, 0, 255)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    LIGHT_YELLOW = (247, 240, 141)

    LIGHT_GREEN = (182, 245, 140)
    DARK_GREEN = (62, 108, 40)
    LIGHT_GRAY = (135, 135, 135)
    LIGHT_BROWN = (217, 192, 104)

    # UI Colours
    PANEL_DARKGREY = (33, 33, 33)
    INFOBOX_GREY = (41, 41, 41)
    INFOBOX_BORDER = (119, 161, 154)
    BUTTON = (220, 242, 239)
    BUTTON_HOVER = (119, 161, 154)
    TEXT_SUBTITLE = (191, 191, 191)
    TEXT_LIGHT = (223, 235, 234)

    # Environment Colours
    LIGHT_BLUE = (185, 237, 234) #(153, 232, 208)
    LIGHT_GRAYBLUE = (97, 133, 145) #(185, 237, 234)
    BLUE = (121, 165, 189)

@dataclass
class Point:
    """
    This dataclass is used to store coordinates. These coordinates may represent the location of an object, a point relevant to an object,
    or any other type of point. This reimplements operations like + - * / since one "position" object represents two numbers: an X and Y coordinate.
    """

    x: int
    y: int

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)
    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)
    def __mul__(self, scalar):
        if isinstance(scalar, self.__class__):
            return Point(self.x * scalar.x, self.y * scalar.y)
        elif isinstance(scalar, tuple):
            return Point(self.x * scalar[0], self.y * scalar[1])
        else:
            return Point(self.x * scalar, self.y * scalar)
    def __truediv__(self, scalar):
        if isinstance(scalar, self.__class__):
            return Point(self.x / scalar.x, self.y / scalar.y)
        elif isinstance(scalar, tuple):
            return Point(self.x / scalar[0], self.y / scalar[1])
        else:
            return Point(self.x / scalar, self.y / scalar)
    def __len__(self):
        return int(math.sqrt(self.x ** 2 + self.y ** 2))
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def tuple(self):
        return (self.x, self.y)

    """
    Unused limit vars
    x_min_limit: int = None
    x_max_limit: int = None
    y_min_limit: int = None
    y_max_limit: int = None
    """

@dataclass
class GameResolution:
    native_res: tuple
    current_res: tuple
    scaling_factor: Point

class Image:
    def __init__(self, filepath, game_res):

        self.scaling_factor = game_res.scaling_factor

        self.image = pygame.image.load(filepath).convert_alpha()

        if(not self.scaling_factor == Point(1, 1)):
            # Use smoothscale if this gets too ugly
            self.image = pygame.transform.scale(self.image, (Point(self.image.get_width(), self.image.get_height()) * self.scaling_factor).tuple())

    def return_scaled_image(self):
        return self.image

    def get_rect(self):
        return self.image.get_rect()

    def render(self, screen, pos: Point, centered = False):
        render_pos = pos * self.scaling_factor # Multiply current position by scaling factor to obtain final position
        if centered:
            render_pos -= Point(self.image.get_width() / 2, self.image.get_height() / 2)
        screen.blit(self.image, render_pos.tuple())


class AnimatedImage():
    def __init__(self, image_directory, frame_length, game_res):

        self.frames = []
        for filepath in glob.glob(f"{image_directory}/*.png"):
            self.frames.append(Image(filepath, game_res))

        self.num_frames = len(self.frames)
        self.current_frame = 0

        self.frame_length = frame_length
        self.time_until_next = self.frame_length
        self.pause = False

    def get_rect(self):
        self.frames[self.current_frame].get_rect()

    def next_frame(self):
        if not self.pause:
            if self.current_frame >= self.num_frames - 1:
                self.current_frame = 0
            else:
                self.current_frame += 1

    def tick(self, delta):
        self.time_until_next -= delta

        if(self.time_until_next <= 0):
            self.next_frame()
            self.time_until_next = self.frame_length

    def render(self, screen, pos: Point, centered = False):
        self.frames[self.current_frame].render(screen, pos, centered)