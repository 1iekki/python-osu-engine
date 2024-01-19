'''
Module for a panel asking a user whether he wants to quit the game
'''

import pygame    
import sys
from modules.gameStateManager import GameStateManager
class AskQuit:
    def __init__(self, screen: pygame.Surface, 
                 gameState: GameStateManager):
        self.screen = screen
        self.window = self.screen.get_rect()
        self.gameState = gameState
    def run(self):
        '''
        Method used to call this panel in the main loop
        '''
        BLACK = pygame.Color("Black")
        WHITE = pygame.Color("White")

        self.screen.fill(BLACK)
        text_font = pygame.font.Font('freesansbold.ttf', 64)
        text_text = text_font.render(f"DO YOU WANT TO QUIT?", True, WHITE)
        text_box = text_text.get_rect()
        text_box.centerx = self.window.centerx
        
        info1_font = pygame.font.Font('freesansbold.ttf', 48)
        info1_text = info1_font.render(f"Press ESC to exit",
                                       True, WHITE)
        info1_box = info1_text.get_rect()
        info1_box.centerx = self.window.centerx
        info1_box.top = text_box.bottom
        
        info2_font = pygame.font.Font('freesansbold.ttf', 48)
        info2_text = info2_font.render(f"Press any key to cancel", 
                                        True, WHITE)
        info2_box = info2_text.get_rect()
        info2_box.centerx = self.window.centerx
        info2_box.top = info1_box.bottom
        self.screen.blit(text_text, text_box)
        self.screen.blit(info1_text, info1_box)
        self.screen.blit(info2_text, info2_box)

        self.controls()

    def controls(self):
        '''
        Controls for the panel
        '''
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                else:
                    self.gameState.set_state("MainMenu")
    
