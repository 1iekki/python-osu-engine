import pygame
import sys
from modules.gameStateManager import GameStateManager
from modules.buttons import Button

class MainMenu:
    
    
    def __init__(self, screen: pygame.Surface, gameState: GameStateManager):

        MARGIN = 30
        WHITE = pygame.Color("White")

        self.screen = screen
        self.window = screen.get_rect()
        self.gameState = gameState
        self.startIMG = pygame.image.load("images/start_button.png")
        self.htpIMG = pygame.image.load("images/htp_button.png")
        self.creditsIMG = pygame.image.load("images/credits_button.png")
        self.quitIMG = pygame.image.load("images/quit_button.png")
        self.startButton = Button(self.startIMG)
        self.htpButton = Button(self.htpIMG)
        self.creditsButton = Button(self.creditsIMG)
        self.quitButton = Button(self.quitIMG)

        self.screen.fill(pygame.Color("Black"))
        
        self.text_font = pygame.font.Font('freesansbold.ttf', 64)
        self.text_text = self.text_font.render(f"RYTHM GAME", True, WHITE)
        self.text_box = self.text_text.get_rect()
        self.text_box.centerx = self.window.centerx
        self.text_box.top = self.window.top + MARGIN

        buttonHeight = self.startIMG.get_height()
        startPos = (self.window.centerx, 
                    self.text_box.top + MARGIN + buttonHeight)
        htpPos = (startPos[0], 
                  startPos[1] + MARGIN + buttonHeight)
        creditsPos = (htpPos[0], 
                      htpPos[1] + MARGIN + buttonHeight)
        quitPos = (creditsPos[0], 
                   creditsPos[1] + MARGIN + buttonHeight)
        
        self.startButton.set_pos(startPos)
        self.htpButton.set_pos(htpPos)
        self.creditsButton.set_pos(creditsPos)
        self.quitButton.set_pos(quitPos)


    def run(self):
        MARGIN = 30

        BLACK = pygame.Color("Black")

        pygame.display.set_caption("Main Menu")
        
        self.screen.fill(BLACK)
        self.screen.blit(self.text_text, self.text_box)
        self.startButton.draw(self.screen)
        self.htpButton.draw(self.screen)
        self.creditsButton.draw(self.screen)
        self.quitButton.draw(self.screen)

        self.startButton.onClick(self.gameState.set_state, "LevelSelection")
        self.htpButton.onClick(self.gameState.set_state, "HowTo")
        self.creditsButton.onClick(self.gameState.set_state, "Credits")
        self.quitButton.onClick(self.quit)
        self.controls()

    def quit(self):
        pygame.quit()
        sys.exit()

    def controls(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.gameState.set_state("AskQuit")