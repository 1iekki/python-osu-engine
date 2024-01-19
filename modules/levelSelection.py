'''
Module containing level selection panel.
'''

import pygame
import sys
import os
from zipfile import ZipFile
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
        for file in os.listdir(f"./"):
            if file.endswith(".osz"):
                with ZipFile(file) as file:
                    name = file.filename
                    name = name[0:-4]
                    file.extractall(f"beatmaps/{name}")
        self.beatmaps = beatmap_parser.search("beatmaps")
        self.playMap = playMap
        self.roullettePos = 0
        self.containers = []
        for bmap in self.beatmaps:
            if bmap.generalData['Mode'] == '0':
                self.containers.append(Container(bmap))
        self.conx = int(self.screen.get_width() * 0.5)
        self.cony = int(self.screen.get_height() * 0.15)
        self.scaledconx = int(self.conx * 1.1)
        self.scaledcony = int(self.cony * 1.1)
        for i, cont in enumerate(self.containers):
            cont.set_dimensions(self.conx, self.cony)

        self.limit = 5
        self.scroll = None
        self.scrollbar = None



    def run(self):
        '''
        Run method dispalys the panel on the screen.
        '''
        
        pygame.display.set_caption("Level Selection")
        WHITE = pygame.Color("White")
        GRAY = (95, 95, 95)
        
        if len(self.containers) == 0:
            return

        self.screen.fill(pygame.Color("Black"))
        text_font = pygame.font.Font('freesansbold.ttf', 64)
        text_text = text_font.render(f"SELECT LEVEL", True, WHITE)
        text_box = text_text.get_rect()
        text_box.centerx = self.window.centerx
        text_box.top = self.window.top
        self.screen.blit(text_text, text_box)

        for i,cont in enumerate(self.containers[
          self.roullettePos : self.roullettePos + self.limit]):
            h = cont.containerBox.h
            offset = h / 2
            cont.set_pos(self.window.centerx, 
                         self.window.top + text_box.h + \
                         offset + h * i + self.margin * i)
            cont.draw(self.screen)
        self.controls()

        if len(self.containers) < self.roullettePos:
            self.roullettePos = 0

        if self.roullettePos + self.limit > len(self.containers):
            self.roullettePos -= 1
        
        if self.roullettePos < 0:
            self.roullettePos = 0

        firstbox = self.containers[self.roullettePos].containerBox
        scrollbar_h = firstbox.h * self.limit
        scroll_w = int(0.01*self.window.w)
        scrollbar = pygame.Rect(0, 0, scroll_w, scrollbar_h)
        scrollbar.left = firstbox.right + self.margin
        scrollbar.top = text_box.bottom
        scroll_h = scrollbar_h if len(self.containers) < self.limit \
            else int(scrollbar_h / len(self.containers))
        scroll = pygame.Rect(0, 0, scroll_w, scroll_h)
        scroll.centerx = scrollbar.centerx
        scroll.top = scrollbar.top + scroll.h * self.roullettePos 
        pygame.draw.rect(self.screen, GRAY, scrollbar)
        pygame.draw.rect(self.screen, WHITE, scroll)

    def load_maps(self):
        '''
        Loads the maps from the main directory.
        It is called only when initializing the class.
        '''
        
        for map in os.listdir("./"):
            if map.endswith(".osz"):
                try:
                    with ZipFile(map) as file:
                        name = file.filename
                        name = name[0:-4]
                        file.extractall(f"beatmaps/{name}")
                except:
                    continue

    def controls(self):
        '''
        Method responsible for handling user inputs.
        '''
        
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
                if event.precise_y < 0:
                    self.roullettePos += 1
                if event.precise_y > 0:
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
