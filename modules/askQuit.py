import pygame    
import sys

class AskQuit:
    def __init__(self, screen, gameState):
        self.screen = screen
        self.window = self.screen.get_rect()
        self.gameState = gameState
    def run(self):
        BLACK = pygame.Color("Black")
        WHITE = pygame.Color("White")

        self.screen.fill(BLACK)
        text_font = pygame.font.Font('freesansbold.ttf', 64)
        text_text = text_font.render(f"DO YOU WANT TO QUIT?", True, WHITE)
        text_box = text_text.get_rect()
        text_box.centerx = self.window.centerx
        self.screen.blit(text_text, text_box)
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
                
    
