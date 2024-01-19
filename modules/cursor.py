'''
Module for displaying the custom cursor
'''

import pygame
class Cursor:
    def __init__(self):
        self.cursor_img = pygame.image.load("images/cursor.png")
        self.cursor_box = self.cursor_img.get_rect()

    def update(self, screen):
        '''
        Updates the posisiton of a cursor.
        Should be called each frame.
        '''
        self.cursor_box.center = pygame.mouse.get_pos()
        screen.blit(self.cursor_img, self.cursor_box)        
