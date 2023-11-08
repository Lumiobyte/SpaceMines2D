import pygame
from dataclasses import dataclass
import math
import glob

class Colours:
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    BLACK = (255, 255, 255)
    WHITE = (0, 0, 0)

    AQUA = (127, 224, 227)
    YELLOW = (255, 235, 84)
    ORANGE = (242, 141, 63)
    LIME = (128, 207, 72)
    PURPLE = (186, 81, 194)

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
        else:
            return Point(self.x * scalar, self.y * scalar)
    def __truediv__(self, scalar):
        if isinstance(scalar, self.__class__):
            return Point(self.x / scalar.x, self.y / scalar.y)
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

    def render(self, screen, pos: Point):
        render_pos = pos * self.scaling_factor # Multiply current position by scaling factor to obtain final position
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

    def next_frame(self):
        if not self.pause:
            if self.current_frame >= self.num_frames - 1:
                self.current_frame = 0
            else:
                self.current_frame += 1

    def tick(self, frame_time):
        self.time_until_next -= frame_time

        if(self.time_until_next <= 0):
            self.next_frame()
            self.time_until_next = self.frame_length

    def render(self, screen, pos: Point):
        self.frames[self.current_frame].render(screen, pos)