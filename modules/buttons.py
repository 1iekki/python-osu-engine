'''
This is a library for the game Click!
This library contains button object and methods for event handling

Made by Eryk Dudkiewicz
'''

import pygame
from typing import Callable


class Button:
    '''
    This is a class for button objects
    Its constructor takes position argument as a tuple,
    image as a pygame.image type object and scale as a float
    '''

    def __init__(self, image: pygame.image, scale: float = 1.0):
        self.scale = scale
        self.width = int(image.get_width()*scale)
        self.height = int(image.get_height()*scale)
        self.image = pygame.transform.scale(image,
                                            (self.width, self.height))
        self.rect = self.image.get_rect()
        self.clicked = False
        self.hovered = False

    def set_pos(self, cords: tuple):
        '''
        Sets the position of the button
        '''
        self.rect.center = cords

    def draw(self, screen : pygame.surface):
        '''
        Draws the object on the screen
        '''
        screen.blit(self.image, self.rect)

    def scale(self, scale : float):
        '''
        Scales the button by a given scale
        '''
        self.width = int(self.image.get_width()*scale)
        self.height = int(self.image.get_height()*scale)
        self.image = pygame.transform.scale(
                        self.image, (self.width, self.height))
        self.rect = self.image.get_rect()

    def onClick(self, action: Callable, arg=None):
        '''
        This method checks if the user clicked the button
        and calls the function specified by the argument action
        '''
        pos = pygame.mouse.get_pos()
        collision = self.rect.collidepoint(pos)
        if collision:
            if pygame.mouse.get_pressed()[0] == 1 \
               and self.clicked is False:
                self.clicked = True
                if arg:
                    return action(arg)
                else: 
                    return action()
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False


if __name__ == "__main__":

    import sys

    def test_func(str=""):
        print("clicked" + str[0])

    pygame.init()
    scr = pygame.display.set_mode((800, 600))
    win = scr.get_rect()

    test_img = pygame.image.load("images/start_button.png")
    test_button = Button(test_img)
    test_button.draw(scr)

    pygame.display.flip()

    while True:
        test_button.onClick(test_func, ["jajko"])
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
