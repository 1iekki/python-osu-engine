import pygame
import pickle
from modules.cursor import Cursor
from modules.gameStateManager import GameStateManager
from modules.mainMenu import MainMenu
from modules.playMap import PlayMap
from modules.levelSelection import LevelSelection
from modules.askQuit import AskQuit
from modules.howToScreen import HowToScreen
from modules.creditsScreen import CreditsScreen
class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.set_num_channels(2)
        pygame.mouse.set_visible(False)
        with open("bin/setup.pkl", "rb") as file:
            self.settings = pickle.load(file)

        self.screen = pygame.display.set_mode(
            self.settings["SCREEN_RESOLUTION"],
            self.settings["SCREEN_FLAGS"],
            self.settings['SCREEN_DEPTH']
        )
        self.fpsCap = self.settings["FPS_CAP"]
        
        self.cursor = Cursor()
        self.clock = pygame.time.Clock()
        self.gameState = GameStateManager()
        self.mainMenu = MainMenu(self.screen, self.gameState) 
        self.playMap = PlayMap(self.screen, self.gameState,
                               self.clock, self.settings,
                               self.cursor)
        self.levelSelection = LevelSelection(self.screen,
                                             self.gameState, self.playMap)
        self.askQuit = AskQuit(self.screen, self.gameState)
        self.howTo = HowToScreen()
        self.credits = CreditsScreen()
        self.STATES = {"MainMenu": self.mainMenu,
                       "LevelSelection": self.levelSelection,
                       "PlayMap": self.playMap,
                       "AskQuit": self.askQuit,
                       "HowTo": self.howTo,
                       "Credits": self.credits
                      }

    def run(self):
        self.gameState.set_state("MainMenu")
        while True:
            # dont place any code here, any changes should be made
            # in run methods of level objects specified in STATES

            currentState = self.STATES[self.gameState.get_state()]            
            currentState.run()
            self.cursor.update(self.screen)
            pygame.display.flip()
            self.clock.tick(self.fpsCap)
