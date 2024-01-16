import pygame
import sys
from modules.gameStateManager import GameStateManager
from modules.playMap import PlayMap
from modules.container import Container
import modules.beatmap_parser as beatmap_parser

class LevelSelection:
    def __init__(self, screen: pygame.Surface, 
                 gameState: GameStateManager, playMap: PlayMap):
        
        self.margin = 5
        self.screen = screen
        self.window = screen.get_rect()
        self.gameState = gameState
        self.beatmaps = beatmap_parser.search("beatmaps")
        self.playMap = playMap
        self.roullettePos = 0
        self.containers = [Container(bmap) for bmap in self.beatmaps]
        self.conx = int(self.screen.get_width() * 0.5)
        self.cony = int(self.screen.get_height() * 0.15)
        self.scaledconx = int(self.conx * 1.1)
        self.scaledcony = int(self.cony * 1.1)
        for i, cont in enumerate(self.containers):
            cont.set_dimensions(self.conx, self.cony)
        self.limit = 5

    def run(self):
        pygame.display.set_caption("Level Selection")
        self.screen.fill(pygame.Color("Black"))
        
        if len(self.containers) == 0:
            return

        if len(self.containers) < self.roullettePos:
            self.roullettePos = [0]

        if self.roullettePos + self.limit > len(self.containers):
            self.roullettePos -= 1
            return
        
        for i,cont in enumerate(self.containers[
          self.roullettePos : self.roullettePos + self.limit]):
            h = cont.containerBox.h
            offset = h / 2
            cont.set_pos(self.window.centerx, 
                         self.window.top + offset + h * i + self.margin)
            cont.draw(self.screen)
        self.controls()

    def controls(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.gameState.set_state("MainMenu")
                if event.key == pygame.K_DOWN:
                    self.roullettePos += 1
                if event.key == pygame.K_UP:
                    self.roullettePos -= 1
            if event.type == pygame.MOUSEWHEEL:
                if event.precise_Y < 0:
                    self.roullettePos += 1
                if event.precise_Y > 0:
                    self.roullettePos -= 1
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for cont in self.containers[
                      self.roullettePos : 
                      self.roullettePos + self.limit]:
                        pos = pygame.mouse.get_pos()
                        collision = cont.containerBox.collidepoint(pos)
                        if collision:
                            self.playMap.set_map(cont.map)
                            self.gameState.set_state("PlayMap")
