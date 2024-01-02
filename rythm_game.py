import pygame
import pickle
import sys
import beatmap_parser as parser

class GameStateManager:
    def __init__(self, *, state="MainMenu"):
        self.state = state

    def get_state(self):
        return self.state

    def set_state(self, state):
        self.state = state
        return self.state

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

class PlayMap:
    def __init__(self, screen: pygame.surface,
                 gameState: GameStateManager, 
                 clock: pygame.time.Clock,
                 settings: dict):
        
        playField = settings["PLAYFIELD_DIMENSIONS"]
        fpsCap = settings["FPS_CAP"]
        margin = settings["PLAYFIELD_MARGIN"]
        self.screen = screen
        self.window = self.screen.get_rect()
        self.gameState = gameState
        self.clock = clock
        self.fpsCap = fpsCap
        self.map = None
        self.hitObjects = None
        self.music = None
        self.circleSize = None
        self.rendered = 0
        self.ogPlayField = playField
        self.scale_factor = (self.window.h - margin) / float(playField[1])
        self.playField = (int(playField[0]*self.scale_factor),
                          int(playField[1]*self.scale_factor - margin))
        self.pos_x = int(self.window.center[0] 
                         - (self.playField[0] / 2))
        self.pos_y = int(self.window.center[1] 
                         - (self.playField[1] / 2))        
        self.hitQueue = []
        self.comboBreak = True
        self.combo = 0
        self.score = 0
        self.clicked = {"INPUT_KEY_1": False, "INPUT_KEY_2": False}
        self.controls = {"INPUT_KEY_1": settings["INPUT_KEY_1"], "INPUT_KEY_2": settings["INPUT_KEY_2"]}
        self.clickTime = 0

    def set_map(self, map: parser.Beatmap):
        self.map = map
        self.hitObjects = map.get_hitobjects()
        self.music = map.get_audio()
        
        size = self.map.circleSize * self.scale_factor * 2
        self.circleSize = (size, size)     
        self.hitCircleIMG = pygame.image.load("images/hitcircle.png")
        self.approachCircle = pygame.image.load("images/approachcircle.png")

    def run(self):
        pygame.draw.rect(self.screen, (255,255,255), ((self.pos_x, self.pos_y), (self.playField)))
        
        pygame.mixer.music.load(self.music)
        pygame.mixer.music.play()
        pygame.mixer.music.set_pos(0)
        while pygame.mixer.music.get_busy():
            self.render_hitobjects()
            self.get_inputs()
            self.eval_hits()
            pygame.display.flip()
    
    def render_hitobjects(self):
        if self.rendered < len(self.hitObjects):
            hitTime = self.hitObjects[self.rendered].showTime
            musicTime = pygame.mixer.music.get_pos()
            if hitTime <= musicTime:         
                self.hitQueue.append(self.hitObjects[self.rendered])
                self.rendered += 1

        self.screen.fill(pygame.Color("Black"))
        for index, hit in enumerate(self.hitQueue):
            if musicTime >= hit.showTime + hit.preempt:
                self.hitQueue.remove(hit)
                continue 
            
            if index in range(1, len(self.hitQueue)):
                pass
            
            if hit.type ['HITCIRCLE']:
                x = hit.x * self.scale_factor
                y = hit.y * self.scale_factor
                x += self.pos_x
                y += self.pos_y
                x = int(x)
                y = int(y)

                relTime = musicTime - hit.showTime
                
                opacity = relTime/float(hit.fadeIn)
                opacity = 255 if opacity > 1.0 else int(255*opacity)

                ac_size = relTime/float(hit.preempt)
                size = self.circleSize[0]
                ac_size = self.circleSize if ac_size >= 1.0 \
                else (int((2.0 - ac_size) * size), int((2.0 - ac_size) * size))
                ac = pygame.transform.scale(self.approachCircle, ac_size)
                ac.convert_alpha()
                ac.set_alpha(opacity)
                ac_box = ac.get_rect()
                ac_box.center = (x, y)
                img = pygame.transform.scale(self.hitCircleIMG, self.circleSize)
                img.convert_alpha()
                img.set_alpha(opacity)
                img_box = img.get_rect()
                img_box.center = (x, y)
                self.screen.blit(img, img_box)
                self.screen.blit(ac, ac_box)
                

    def get_inputs(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == self.controls["INPUT_KEY_1"]:
                    if self.clicked["INPUT_KEY_1"] == False:
                        self.clickTime = pygame.mixer.music.get_pos()
                        self.clicked["INPUT_KEY_1"] = True
                if event.key == self.controls["INPUT_KEY_2"]:
                    if self.clicked["INPUT_KEY_2"] == False:
                        self.clickTime = pygame.mixer.music.get_pos()
                        self.clicked["INPUT_KEY_2"] = True
            if event.type == pygame.KEYUP:
                self.clicked["INPUT_KEY_1"] = False
                self.clicked["INPUT_KEY_1"] = False


    def eval_hits(self):
        pass

class LevelSelection:
    def __init__(self, screen: pygame.Surface, 
                 gameState: GameStateManager, playMap: PlayMap):
        self.screen = screen
        self.gameState = gameState
        self.beatmaps = parser.search("beatmaps")
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
                    self.playMap.set_map(self.beatmaps[1])
                    self.gameState.set_state("PlayMap")

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        with open("bin/setup.pkl", "rb") as file:
            self.settings = pickle.load(file)

        self.screen = pygame.display.set_mode(
            self.settings["SCREEN_RESOLUTION"],
            self.settings["SCREEN_FLAGS"],
            self.settings['SCREEN_DEPTH']
        )
        self.fpsCap = self.settings["FPS_CAP"]
        
        self.clock = pygame.time.Clock()
        self.gameState = GameStateManager()
        self.mainMenu = MainMenu(self.screen, self.gameState) 
        self.playMap = PlayMap(self.screen, self.gameState,
                               self.clock, self.settings)
        self.levelSelection = LevelSelection(self.screen,
                                             self.gameState, self.playMap)

        self.STATES = {"MainMenu": self.mainMenu,
                       "LevelSelection": self.levelSelection,
                       "PlayMap": self.playMap 
                      }

    def run(self):
        self.gameState.set_state("LevelSelection")
        while True:
            # dont place any code here, any changes should be made
            # in run methods of level objects specified in STATES

            currentState = self.STATES[self.gameState.get_state()]            
            currentState.run()
            pygame.display.flip()
            self.clock.tick(self.fpsCap)


def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()