import pygame
import pickle
import sys
import beatmap_parser as parser

class Cursor:
    def __init__(self, screen):
        self.cursor_img = pygame.image.load("images/cursor.png")
        self.cursor_box = self.cursor_img.get_rect()
        self.screen = screen

    def update(self):
        self.cursor_box.center = pygame.mouse.get_pos()
        self.screen.blit(self.cursor_img, self.cursor_box)        

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
                 settings: dict,
                 cursor: Cursor):
        
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
        self.circleSize = None
        self.music = None
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
        self.combo = 1
        self.score = 0
        self.rendered = 0
        self.clickTime = 0
        self.clicked = {"INPUT_KEY_1": False, "INPUT_KEY_2": False}
        self.controls = {"INPUT_KEY_1": settings["INPUT_KEY_1"], "INPUT_KEY_2": settings["INPUT_KEY_2"]}
        self.cursor = cursor
        self.soundChannel = pygame.mixer.Channel(0)
        self.hit50 = 0
        self.hit100 = 0
        self.hit300 = 0
        self.miss = 0
        self.all = 0


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
            self.show_score()
            self.cursor.update()
            pygame.display.flip()
    
    def show_score(self):
        score_font = pygame.font.Font('freesansbold.ttf', 48)
        score_text = score_font.render(f"{self.score}", True, pygame.color.Color("White"))
        score_box = score_text.get_rect()
        score_box.centerx = self.window.centerx
        score_box.top = self.window.top + 8
        
        combo_text = score_font.render(f"{self.combo}X", True, pygame.color.Color("White"))
        combo_box = score_text.get_rect()
        combo_box.bottomleft = self.window.bottomleft

        acc = 0 if self.all == 0 \
                else (self.hit300 * 3 
                      + self.hit100 * 2 
                      + self.hit50) / self.all * 100

        acc_text = score_font.render(f"{acc:.2f}%", True, pygame.color.Color("White"))
        acc_box = acc_text.get_rect()
        acc_box.topright = self.window.topright
        
        self.screen.blit(score_text, score_box)
        self.screen.blit(combo_text, combo_box)
        self.screen.blit(acc_text, acc_box)

    def render_hitobjects(self):
        if self.rendered < len(self.hitObjects):
            hitTime = self.hitObjects[self.rendered].showTime
            musicTime = pygame.mixer.music.get_pos()
            if hitTime <= musicTime:         
                self.hitQueue.append(self.hitObjects[self.rendered])
                self.rendered += 1

        self.screen.fill(pygame.Color("Black"))
        queue = reversed(self.hitQueue)
        for hit in queue:
            if musicTime >= hit.showTime + hit.preempt + hit.hitWindow['50']:
                self.hitQueue.remove(hit)
                self.miss += 1
                self.all += 3
                self.combo = 1
                continue 

            # if hit.type ['HITCIRCLE']:
            x = hit.x * self.scale_factor
            y = hit.y * self.scale_factor
            x += self.pos_x
            y += self.pos_y
            x = int(x)
            y = int(y)

            relTime = musicTime - hit.showTime
            fadeIN = relTime/float(hit.fadeIn)
            fadeOUT = (relTime - hit.preempt) \
                / float(hit.hitWindow['50'])

            if relTime < hit.preempt:
                opacity = 255 if fadeIN > 1.0 else int(255*fadeIN)
            else:
                opacity = int(255 - 255 * fadeOUT)               

            ac_size = relTime/float(hit.preempt)
            size = self.circleSize[0]
            ac_size = self.circleSize if ac_size >= 1.0 \
                else (int((2.0 - ac_size) * size),
                        int((2.0 - ac_size) * size))
            ac = pygame.transform.smoothscale(self.approachCircle, ac_size)
            ac.convert_alpha()
            ac.set_alpha(opacity)
            ac_box = ac.get_rect()
            ac_box.center = (x, y)
            img = pygame.transform.smoothscale(self.hitCircleIMG, self.circleSize)
            img.convert_alpha()
            img.set_alpha(opacity)
            img_box = img.get_rect()
            img_box.center = (x, y)
            self.screen.blit(img, img_box)
            self.screen.blit(ac, ac_box)
            hit.hitbox = img_box
                

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
                        scored = self.eval_hits()
                        if scored == -1: continue
                        if self.comboBreak:
                            self.combo = 1
                        else:
                            self.combo += 1
                        self.score += self.combo * scored
                if event.key == self.controls["INPUT_KEY_2"]:
                    if self.clicked["INPUT_KEY_2"] == False:
                        self.clickTime = pygame.mixer.music.get_pos()
                        self.clicked["INPUT_KEY_2"] = True
                        scored = self.eval_hits()
                        if scored == 0:
                            if scored == -1: continue
                            self.combo = 1
                            self.score += self.combo * scored
            if event.type == pygame.KEYUP:
                self.clicked["INPUT_KEY_1"] = False
                self.clicked["INPUT_KEY_2"] = False


    def eval_hits(self) -> int:
        musicTime = pygame.mixer.music.get_pos()
        cursorPos = pygame.mouse.get_pos()
        if len(self.hitQueue) < 1:
            return -1
        hit = self.hitQueue[0]
        collision = hit.hitbox.collidepoint(cursorPos)
        if collision:
            if musicTime < hit.time - hit.hitWindow['50']:
                self.comboBreak = True
                self.hitQueue.pop(0)
                self.all += 3
                self.miss += 1
                return 0
            if musicTime > hit.time - hit.hitWindow['50'] \
                and musicTime < hit.time - hit.hitWindow['100']:
                self.comboBreak = False
                self.hitQueue.pop(0)
                self.all += 3
                self.hit50 += 1
                return 50
            if musicTime > hit.time - hit.hitWindow['100'] \
                and musicTime < hit.time - hit.hitWindow['300']:
                self.comboBreak = False
                self.hitQueue.pop(0)
                self.all += 3
                self.hit100 += 1
                return 100
            if musicTime > hit.time - hit.hitWindow['300'] \
                and musicTime < hit.time + hit.hitWindow['300']:
                self.comboBreak = False
                self.hitQueue.pop(0)
                self.all += 3
                self.hit300 += 1
                return 300
            if musicTime > hit.time + hit.hitWindow['300'] \
                and musicTime < hit.time + hit.hitWindow['100']:
                self.comboBreak = False
                self.hitQueue.pop(0)
                self.all += 3
                self.hit100 += 1
                return 100
            if musicTime > hit.time + hit.hitWindow['100'] \
                and musicTime < hit.time + hit.hitWindow['50']:
                self.comboBreak = False
                self.hitQueue.pop(0)
                self.all += 3
                self.hit50 += 1
                return 50
            if musicTime > hit.time + hit.hitWindow['50']:
                self.comboBreak = True
                self.hitQueue.pop(0)
                self.all += 3
                self.miss += 1
                return 0
        return -1
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
                    self.playMap.set_map(self.beatmaps[2])
                    self.gameState.set_state("PlayMap")

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
        
        self.cursor = Cursor(self.screen)
        self.clock = pygame.time.Clock()
        self.gameState = GameStateManager()
        self.mainMenu = MainMenu(self.screen, self.gameState) 
        self.playMap = PlayMap(self.screen, self.gameState,
                               self.clock, self.settings,
                               self.cursor)
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
            self.cursor.update()
            pygame.display.flip()
            self.clock.tick(self.fpsCap)


def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()