import pygame
import sys
from modules.gameStateManager import GameStateManager

class MainMenu:
    def __init__(self, screen: pygame.Surface, gameState: GameStateManager):
        self.screen = screen
        self.gameState = gameState

    def run(self):
        self.screen.fill(pygame.Color("Black"))
        
        self.controls()

    def controls(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()