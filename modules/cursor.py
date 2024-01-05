import pygame
class Cursor:
    def __init__(self, screen):
        self.cursor_img = pygame.image.load("images/cursor.png")
        self.cursor_box = self.cursor_img.get_rect()
        self.screen = screen

    def update(self):
        self.cursor_box.center = pygame.mouse.get_pos()
        self.screen.blit(self.cursor_img, self.cursor_box)        
