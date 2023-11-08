import pygame

class Text():
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