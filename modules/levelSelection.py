import pygame
import sys
from modules.gameStateManager import GameStateManager
from modules.playMap import PlayMap
import modules.beatmap_parser as beatmap_parser

class LevelSelection:
    def __init__(self, screen: pygame.Surface, 
                 gameState: GameStateManager, playMap: PlayMap):
        self.screen = screen
        self.gameState = gameState
        self.beatmaps = beatmap_parser.search("beatmaps")
        self.playMap = playMap

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
                if event.key == pygame.K_c:
                    self.playMap.set_map(self.beatmaps[0])
                    self.gameState.set_state("PlayMap")
