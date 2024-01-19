'''
Module containing how to play panel.
'''

import pygame    
import sys
from modules.gameStateManager import GameStateManager
class HowToScreen:
    def __init__(self, screen: pygame.Surface, 
                 gameState: GameStateManager):
        self.screen = screen
        self.window = self.screen.get_rect()
        self.gameState = gameState
        self.page = 1
        self.pages = {
            1: [
            "",
            "1. IMPORTING MAPS",
            "",
            "To import a map place the beatmap file "
            "(with .osz extension) in the game folder",
            "The maps import on game start, so if they didn't import, ",
            "simply restart the game",
            "",
            "SELECTING MAPS",
            "",
            "After clicking start you will see a level selection screen.",
            "Click on a map you want to play, use scroll to see more maps.",
            "The map is described by the title of the song on top,",
            "the artist, and the creator of the map in the second line,",
            "and the difficulty on the bottom",
            "",
            "Gameplay explanation on another page",
            "Press RIGHT ARROW or SPACE key",
            "",
            "Press ESC to quit"
            ],
            2:  [
            "",
            "2. GAMEPLAY PT.1 : HITCIRCLES",
            "You will see circles appear on screen",
            "The circles appear in sync with the music.",
            "They can match either the beat, "
            "instruments or sometimes vocals.",
            "The circles have a ring around them,"
            " that ring shrinks with time.",
            "This ring helps you hit the circle at the right moment.",
            "When the ring is no longer visible "
            "it's the right moment to click.",
            "Clicking a little bit early, or a little bit late "
            "gives you less points",
            "Points you score get multiplied by the combo.",
            "Combo gets incremented each time you score points",
            "Score is displayed at the top of the sreen.",
            "On the top right corner you can see your accuracy",
            "",
            "More on next page",
            "Press RIGHT ARROW or SPACE key to go forward"
            " or press LEFT ARROW to go back",
            "",
            "Press ESC to quit"
            ],
            3:  [
            "",
            "2. GAMEPLAY PT.2 : SLIDERS",
            "Sliders are special kinds of hitcircles.",
            "They work on the same principle as normal hitcircles, ",
            "but after you click the circle you need to hold the key ",
            "and keep your cursor inside the ring, which follows the slider path",
            "to the end of the slider.",
            "Sliders can bounce, which means after they reach the end, ",
            "they reverse and go to another end.",
            "This can happen multiple times.",
            "Whether or not the slider will bounce is marked by ",
            "a reverse arrow symbol at the end of the slider.",
            "Sliders are less strict when it comes to clicking late or early.",
            "However, moving your mouse out of the ring applies penalties ",
            "and if you're out of the ring for too long it will eventually break your combo",
            ""
            "Press LEFT ARROW to go back",
            "",
            "Press ESC to quit"
            ]
        
        
        }

    def run(self):
        '''
        Method used to call this panel in the main loop
        '''
        BLACK = pygame.Color("Black")
        WHITE = pygame.Color("White")
        LINE_H = 10

        self.screen.fill(BLACK)

        text_font = pygame.font.Font('freesansbold.ttf', 24)
        text_str = self.pages[self.page]
        text_box = []
        for i, t in enumerate(text_str):
            text = text_font.render(t, True, WHITE)
            text_box.append(text.get_rect())
            text_box[i].centerx = self.window.centerx
            text_box[i].top = self.window.top + text_box[i].h*i + LINE_H * i
            self.screen.blit(text, text_box[i])

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
                    self.page = 1
                    self.gameState.set_state("MainMenu")
                if event.key in (pygame.K_RIGHT, pygame.K_SPACE):
                    if self.page < 3:
                        self.page += 1
                if event.key == pygame.K_LEFT:
                    if self.page > 1:
                        self.page -= 1
