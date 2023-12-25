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
        self.HitObjects = None
        self.music = None
        self.rendered = 0
        self.ogPlayField = playField
        self.scale_factor = (self.window.h - margin) / float(playField[1])
        self.playField = (int(playField[0]*self.scale_factor),
                          int(playField[1]*self.scale_factor - margin))
        self.pos_x = int(self.window.center[0] 
                         - (self.playField[0] / 2))
        self.pos_y = int(self.window.center[1] 
                         - (self.playField[1] / 2))
        

    def set_map(self, map: parser.Beatmap):
        self.map = map
        self.hitObjects = map.get_hitobjects()
        self.music = map.get_audio()

    def run(self):
        pygame.mixer.music.load(self.music)
        pygame.mixer.music.play()
        pygame.mixer.music.set_pos(0)
        while pygame.mixer.music.get_busy():
            self.render_hitobjects()
            self.get_inputs()
            self.eval_hits()
            # print(pygame.mixer.music.get_pos())
            # pygame.draw.rect(self.screen, (255,255,255), (self.pos_x,self.pos_y,self.playField[0],self.playField[1]))
            pygame.display.flip()
    
    def render_hitobjects(self):
        if self.rendered < len(self.hitObjects):
            print(pygame.mixer.music.get_pos())
            hitTime = self.hitObjects[self.rendered].time
            musicTime = pygame.mixer.music.get_pos()
            if hitTime <= musicTime:
                x = self.hitObjects[self.rendered].x * self.scale_factor
                y = self.hitObjects[self.rendered].y * self.scale_factor
                x += self.pos_x
                y += self.pos_y
                pygame.draw.circle(self.screen, (255,255,255), (x,y), 20)
                self.rendered += 1
                

    def get_inputs(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

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
                    self.playMap.set_map(self.beatmaps[0])
                    self.gameState.set_state("PlayMap")

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        with open("bin/setup.pkl", "rb") as file:
            self.settings = pickle.load(file)

        self.screen = pygame.display.set_mode(
            self.settings["SCREEN_RESOLUTION"],
            self.settings["SCREEN_FLAGS"]
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