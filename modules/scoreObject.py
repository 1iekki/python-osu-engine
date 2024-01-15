import pygame

class ScoreObject:
    def __init__(self, image: pygame.Surface, 
                 box: pygame.rect, appearTime: int,
                 duration: int = 300):
        self.img = image
        self.box = box
        self.appearTime = appearTime
        self.duration = duration
        self.disappearTime = appearTime + duration

    def draw(self, screen: pygame.Surface):
        musicTime = pygame.mixer.music.get_pos()
        relTime = musicTime - self.appearTime
        fadeOUT = relTime/float(self.duration)

        opacity = int(255 - 255 * fadeOUT)   
        self.img.set_alpha(opacity)
        screen.blit(self.img, self.box)