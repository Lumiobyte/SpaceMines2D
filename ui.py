import pygame
from classes import *

class Text:
    def __init__(self, scaling_factor):
        self.TINY = pygame.font.Font("fonts/segoe/segoe-ui.ttf", int(16 * scaling_factor))
        self.SMALL = pygame.font.Font("fonts/segoe/segoe-ui.ttf", int(24 * scaling_factor))
        self.SMALL_BOLD = pygame.font.Font("fonts/segoe/segoe-ui-bold.ttf", int(24 * scaling_factor))
        self.MEDIUM = pygame.font.Font("fonts/segoe/segoe-ui.ttf", int(32 * scaling_factor))
        self.LARGE = pygame.font.Font("fonts/segoe/segoe-ui.ttf", int(48 * scaling_factor))
        self.MED_BOLD = pygame.font.Font("fonts/segoe/segoe-ui-bold.ttf", int(48 * scaling_factor))
        self.LARGE_BOLD = pygame.font.Font("fonts/segoe/segoe-ui-bold.ttf", int(48 * scaling_factor))


    def write(self, screen, font, colour, location, text, centered = False):

        if centered:
            text_render = font.render(text, True, colour)
            screen.blit(text_render, text_render.get_rect(center = location))
        else:
            screen.blit(font.render(text, True, colour), location)

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
    def __init__(self, size: Point, pos: Point, data: dict, animation: ZoomAnimation):

        self.size = size #pygame.Rect(pos.x - shape.width / 2, pos.y - shape.height / 2, shape.width, shape.height) # Rect with left and top adjusted for the desired centerpoint `pos`
        self.pos = pos # Will probably just be screen center most of the time
        self.data = data
        self.animation = animation

        self.newly_opened = True # Tells the infobox that it just switched from closed to open state

        pass

    def open(self, delta):

        self.newly_opened = True # This is later set to false in main function, after the dimming overlay is rendered
        self.animation.play(self.size, delta)

    def process(self, pos, clicks, keys):

        if self.animation and self.animation.playing: # Wait until animation is finished before accepting inputs
            return

        # Process all inputs

        pass

    def render(self, screen, delta):

        infobox_surface = pygame.Surface((self.size.x, self.size.y))

        final_size = self.size
        if self.animation and self.animation.playing:
            final_size = self.animation.play(self.size, delta)

        infobox_surface.fill(Colours.GREEN)
        pygame.draw.circle(infobox_surface, Colours.BLUE, (100, 100), 10)


        infobox_surface = pygame.transform.scale(infobox_surface, final_size.tuple())

        blit_pos = (self.pos.x - (infobox_surface.get_width() / 2), self.pos.y - (infobox_surface.get_height() / 2))
        screen.blit(infobox_surface, blit_pos)

        return pygame.Rect(*blit_pos, self.size.x, self.size.y)
