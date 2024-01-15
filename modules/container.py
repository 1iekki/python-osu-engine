import pygame
from modules.beatmap import Beatmap

class Container:
    def __init__(self, beatmap: Beatmap):
        self.containerIMG = pygame.image.load("images/container.png")
        self.containerBox = self.containerIMG.get_rect()
        self.map = beatmap
        self.mainFontSize = int(self.containerBox.h / 8)
        self.secondaryFontSize = int(self.containerBox.h / 10)
    
    def set_dimensions(self, x: int, y: int):
        self.containerIMG = pygame.transform.smoothscale(
            self.containerIMG, (x, y))
        self.containerBox = self.containerIMG.get_rect()
        self.mainFontSize = int(self.containerBox.h / 8)
        self.secondaryFontSize = int(self.containerBox.h / 10)
    
    def set_pos(self, x: int, y: int):
        self.containerBox.center = (x, y)
    
    def draw(self, screen: pygame.Surface):
        WHITE = pygame.Color("White")

        title_font = pygame.font.Font('freesansbold.ttf', 
                                     self.mainFontSize)
        title_text = title_font.render(f"{self.map.metadata['Title']}", 
                                     True, WHITE)
        title_box = title_text.get_rect()

        desc_font = pygame.font.Font('freesansbold.ttf', 
                                     self.secondaryFontSize)
        string = f"Artist: {self.map.metadata['Artist']} // "
        string += f"Creator: {self.map.metadata['Creator']}"
        desc_text = desc_font.render(string, True, WHITE)
        desc_box = desc_text.get_rect()

        dif_text = desc_font.render(f"{self.map.metadata['Version']}", 
                                    True, WHITE)
        dif_box = dif_text.get_rect()
    
        desc_box.center = self.containerBox.center
        title_box.bottom = desc_box.top
        title_box.centerx = self.containerBox.centerx
        dif_box.centerx = self.containerBox.centerx
        dif_box.top = desc_box.bottom

        screen.blit(self.containerIMG, self.containerBox)        
        screen.blit(title_text, title_box)
        screen.blit(desc_text, desc_box)
        screen.blit(dif_text, dif_box)
        
    
    def onClick(self):
        pass

