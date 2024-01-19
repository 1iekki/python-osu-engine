'''
This module is a panel with the main gameplay.
Beatmap must be set before calling the run method.
'''

import pygame
import sys
from modules.gameStateManager import GameStateManager
from modules.cursor import Cursor
from modules.beatmap_parser import Beatmap
from modules.scoreObject import ScoreObject

class PlayMap:
   
    def __init__(self, screen: pygame.Surface,
                 gameState: GameStateManager, 
                 clock: pygame.time.Clock,
                 settings: dict,
                 cursor: Cursor):
        
        BACKROW_ALPHA = 160
        COMBOBREAK_THRESHOLD = 10

        playField = settings["PLAYFIELD_DIMENSIONS"]
        fpsCap = settings["FPS_CAP"]
        margin = settings["PLAYFIELD_MARGIN"]
        self.screen = screen
        self.window = self.screen.get_rect()
        self.gameState = gameState
        self.clock = clock
        self.fpsCap = fpsCap
        self.map = None
        self.quitGame = False
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
        self.comboBreakTreshold = COMBOBREAK_THRESHOLD
        self.combo = 1
        self.score = 0
        self.rendered = 0
        self.clickTime = 0
        self.clicked = {"INPUT_KEY_1": False, "INPUT_KEY_2": False}
        self.controls = {"INPUT_KEY_1": settings["INPUT_KEY_1"], "INPUT_KEY_2": settings["INPUT_KEY_2"]}
        self.cursor = cursor
        self.soundChannel = pygame.mixer.Channel(0)
        self.soundChannel2 = pygame.mixer.Channel(1)
        self.hit50 = 0
        self.hit100 = 0
        self.hit300 = 0
        self.miss = 0
        self.all = 0
        self.frontRow = self.screen.copy()
        self.backRow = self.screen.copy()
        self.backRow.convert_alpha()
        self.backRow.set_alpha(BACKROW_ALPHA)
        self.sliderColor = (95, 95, 95)
        self.sliderCircleWidth = 2
        self.sliderCircleColor = (255, 255, 255)
        self.hitNum = 1
        self.currentsurf = self.backRow
        self.mousePos = None
        self.scoreQueue = []
        self.musicVolume = settings['MUSIC_VOLUME']
        self.soundVolume = settings['SOUND_VOLUME']

    def reset_vars(self):
        '''
        Resets the variables, so that the map can be played again.
        '''
        
        self.map = None
        self.hitObjects = None
        self.circleSize = None
        self.music = None
        self.mousePos = None
        self.hitNum = 1
        self.hitQueue = []
        self.scoreQueue = []
        self.comboBreak = True
        self.combo = 1
        self.score = 0
        self.rendered = 0
        self.clickTime = 0
        self.hit50 = 0
        self.hit100 = 0
        self.hit300 = 0
        self.miss = 0
        self.all = 0


    def set_map(self, map: Beatmap):
        '''
        Sets a specified map to be played.
        '''
        
        SLIDER_BALL_SCALE = 2

        # get map info
        self.map = map
        self.hitObjects = map.get_hitobjects()
        self.music = map.get_audio()
        
        size = self.map.circleSize * self.scale_factor * 2
        self.circleSize = (size, size)     

        self.sliderFieldSize = (size * SLIDER_BALL_SCALE,
                               size * SLIDER_BALL_SCALE)
        self.hitCircleIMG = pygame.image.load("images/hitcircle.png")
        self.approachCircle = pygame.image.load("images/approachcircle.png")
        self.sliderBounceIMG = pygame.image.load("images/sliderreverse.png")
        self.hitInternal = {1: pygame.image.load("images/1.png"),
                            2: pygame.image.load("images/2.png"),
                            3: pygame.image.load("images/3.png"),
                            4: pygame.image.load("images/4.png"),
                            5: pygame.image.load("images/5.png"),
                            6: pygame.image.load("images/6.png"),
                            7: pygame.image.load("images/7.png"),
                            8: pygame.image.load("images/8.png"),
                            9: pygame.image.load("images/9.png")}
        self.sounds = {
            'hitnormal': pygame.mixer.Sound("hitsounds/normal-hitnormal.wav"),
            'slidertick': pygame.mixer.Sound("hitsounds/normal-slidertick.wav"),
            'combobreak': pygame.mixer.Sound("hitsounds/combobreak.mp3")}
        
        self.scoreImages = {0: pygame.image.load("images/hit0.png"),
                            50: pygame.image.load("images/hit50.png"),
                            100: pygame.image.load("images/hit100.png"),
                            300: pygame.image.load("images/hit300.png")}

    def run(self):
        '''
        Runs the panel.
        This methods stops the execution of the main loop
        until the map is finished or until the player leaves
        '''
        
        pygame.display.set_caption(
            f"Playing: {self.map.name}")

        #init sliders
        for hit in self.hitObjects:
            if hit.type['SLIDER'] is True:
                hit.generate_slider_path(self.scale_factor, self.pos_x, self.pos_y)

        pygame.draw.rect(self.screen, (255,255,255), ((self.pos_x, self.pos_y), (self.playField)))
        pygame.mixer.music.load(self.music)
        pygame.mixer.music.play()
        pygame.mixer.music.set_pos(0)
        pygame.mixer.music.set_volume(0.1)
        self.soundChannel.set_volume(self.musicVolume)
        self.soundChannel2.set_volume(self.soundVolume)
        while pygame.mixer.music.get_busy():
            if self.rendered == len(self.hitObjects) \
                and len(self.hitQueue) == 0:
                pygame.mixer.music.stop()
                continue
            self.render_objects()
            self.get_inputs()
            self.show_score()
            self.cursor.update(self.frontRow)
            self.screen.blit(self.frontRow, (0,0))
            pygame.display.flip()
        if not self.quitGame:
            self.final_screen()

    
    def render_hitcircle(self, hit):
        '''
        Method responsible for rendering a hitcircle on the screen
        '''

        x = hit.x * self.scale_factor
        y = hit.y * self.scale_factor
        x += self.pos_x
        y += self.pos_y
        x = int(x)
        y = int(y)

        self.musicTime = pygame.mixer.music.get_pos()
        relTime = self.musicTime - hit.showTime
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
            else (int((3.0 - ac_size * 2) * size),
                    int((3.0 - ac_size * 2) * size))
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
        hitnum = pygame.transform.smoothscale(self.hitInternal[hit.hitnum], self.circleSize)
        hitnum.convert_alpha()
        hitnum.set_alpha(opacity)
        hitnum_box = img.get_rect()
        hitnum_box.center = (x, y)
        self.currentsurf.blit(hitnum, hitnum_box)
        self.currentsurf.blit(img, img_box)
        self.currentsurf.blit(ac, ac_box)
        hit.hitbox = img_box

    def show_score(self):
        '''
        Method used for displaying the score on the screen.
        '''

        score_font = pygame.font.Font('freesansbold.ttf', 48)
        score_text = score_font.render(f"SCORE: {self.score}", True, pygame.color.Color("White"))
        score_box = score_text.get_rect()
        score_box.centerx = self.window.centerx
        score_box.top = self.window.top
        
        combo_text = score_font.render(f"COMBO: {self.combo}X", True, pygame.color.Color("White"))
        combo_box = score_text.get_rect()
        combo_box.bottomleft = self.window.bottomleft

        self.acc = 0 if self.all == 0 \
                else (self.hit300 * 3 
                      + self.hit100 * 2 
                      + self.hit50) / self.all * 100

        acc_text = score_font.render(f"ACC: {self.acc:.2f}%", True, pygame.color.Color("White"))
        acc_box = acc_text.get_rect()
        acc_box.topright = self.window.topright
        
        self.frontRow.blit(score_text, score_box)
        self.frontRow.blit(combo_text, combo_box)
        self.frontRow.blit(acc_text, acc_box)

    def render_objects(self):
        '''
        Method responsible for managing which objects should be rendered,
        as well as controling the sliders.
        '''
        
        SLIDER_END = 0
        SLIDER_BOUNCES = 2
        SLIDER_ADVANCES = 1

        if self.rendered < len(self.hitObjects):
            hit = self.hitObjects[self.rendered]
            self.musicTime = pygame.mixer.music.get_pos()
            if hit.showTime <= self.musicTime \
                and not hit.type['SPINNER']:         
                self.hitQueue.append(self.hitObjects[self.rendered])
                self.rendered += 1
            if hit.type['SPINNER']:
                self.rendered += 1

        self.screen.fill(pygame.Color("Black"))
        empty = pygame.Color(0,0,0,0)
        self.frontRow.fill(empty)
        self.frontRow.blit(self.backRow, (0, 0))
        self.backRow.fill(empty)

        queue = self.hitQueue.copy()
        queue.reverse()
        for i, hit in enumerate(queue):

            # hitobject numbering
            if hit.hitnum == 0:
                if hit.type['NEWCOMBO'] is True:
                    self.hitNum = 1
                else:
                    self.hitNum += 1
                if self.hitNum > 9:
                    self.hitNum = 1
                hit.hitnum = self.hitNum

            # first hitobject highlighting
            if i == queue.index(queue[-1]):
                self.currentsurf = self.frontRow
            else:
                self.currentsurf = self.backRow

            self.musicTime = pygame.mixer.music.get_pos()

            if hit.type ['HITCIRCLE'] is True:
                
                self.render_hitcircle(hit)

                # remove missed hitcircles
                missTime = hit.showTime + hit.preempt + hit.hitWindow['50']
                if self.musicTime >= missTime:
                    self.miss += 1
                    self.all += 3
                    if self.combo > self.comboBreakTreshold:
                        self.soundChannel2.play(self.sounds['combobreak'])
                    self.combo = 1

                    img = self.scoreImages[0]
                    img_box = img.get_rect()
                    img_box.center = hit.hitbox.center
                    
                    self.scoreQueue.append(ScoreObject(
                        img, img_box, pygame.mixer.music.get_pos()))

                    self.hitQueue.remove(hit)
                    continue 

            if hit.type['SLIDER'] is True:

                # draw slider outline
                path = hit.get_slider_path()
                radius = self.circleSize[0] / 2
                for (x,y) in path:
                    pygame.draw.circle(self.currentsurf, 
                                       self.sliderColor, (x,y), radius)
                pygame.draw.circle(self.currentsurf, 
                                   self.sliderCircleColor, 
                                   path[0], radius, self.sliderCircleWidth)
                pygame.draw.circle(self.currentsurf, 
                                   self.sliderCircleColor, 
                                   path[-1], radius, self.sliderCircleWidth)
                if hit.slides > 1:
                    bounce_img = pygame.transform.smoothscale(
                        self.sliderBounceIMG, self.circleSize)
                    bounce_box = bounce_img.get_rect()
                    bounce_box.center = path[-1]
                    self.currentsurf.blit(bounce_img, bounce_box)

                #slider activation
                if self.musicTime >= hit.hitTime:
                    hit.sliderRuns = True

                #slider movement                
                if hit.sliderRuns is True:
                    relTime = self.musicTime - hit.hitTime
                    control = hit.advance_slider(relTime)
                    
                    if control == SLIDER_END:
                        scored = self.eval_slider_end(hit)
                        self.score += scored * self.combo
                        continue
                    if control == SLIDER_BOUNCES:
                        pos = pygame.mouse.get_pos()
                        collision = hit.hitbox.collidepoint(pos)
                        self.soundChannel.play(self.sounds['hitnormal'])
                        if collision:
                            self.combo += 1
                        else:
                            hit.sliderBreak = True

                    (new_x, new_y) = hit.get_slider_phase()
                    img = pygame.transform.smoothscale(
                        self.hitCircleIMG, self.circleSize)
                    img.convert_alpha()
                    img_box = img.get_rect()
                    img_box.center = (new_x, new_y)
                    ac = pygame.transform.smoothscale(
                        self.approachCircle, self.sliderFieldSize)
                    ac_box = ac.get_rect()
                    ac_box.center = (new_x, new_y)
                    self.currentsurf.blit(ac, ac_box)
                    self.currentsurf.blit(img, img_box)
                    hit.hitbox = ac_box

                    # check mouse on slider
                    pos = pygame.mouse.get_pos()
                    collision = hit.hitbox.collidepoint(pos)
                    tick = hit.sliderTick
                    if not collision:
                        hit.sliderOut = True
                    if relTime - tick * hit.ticks >= tick:
                        hit.ticks += 1
                        if not collision:
                            self.comboBreak = True
                            hit.sliderBreak = True
                        else:
                            self.combo += 1
                else:
                    self.render_hitcircle(hit)

        for obj in self.scoreQueue:
            if self.musicTime >= obj.disappearTime:
                self.scoreQueue.remove(obj)
                continue
            obj.draw(self.frontRow)

    def final_screen(self):
        '''
        Method responsible for displaying the final screen 
        after completing the map.
        '''

        BLACK = pygame.Color("Black")
        WHITE = pygame.Color("White")
        pygame.mixer.music.pause()
        
        paused = True
        while paused:
            self.screen.fill(BLACK)
            text_font = pygame.font.Font('freesansbold.ttf', 64)
            text_text = text_font.render(f"CONGRATULATIONS!", True, WHITE)
            text_box = text_text.get_rect()
            text_box.centerx = self.window.centerx
            text_box.top = self.window.top
            info1_font = pygame.font.Font('freesansbold.ttf', 48)
            info1_text = info1_font.render(f"Press ESC to go back",
                                            True, WHITE)
            info1_box = info1_text.get_rect()
            info1_box.centerx = self.window.centerx
            info1_box.top = text_box.bottom

            info2_font = pygame.font.Font('freesansbold.ttf', 36)
            info2_text = info2_font.render(f"Accuracy: {self.acc:.2f}%", 
                                           True, WHITE)
            info2_box = info2_text.get_rect()
            info2_box.centerx = self.window.centerx
            info2_box.top = info1_box.bottom


            info3_font = pygame.font.Font('freesansbold.ttf', 36)
            info3_text = info3_font.render(f"Miss: {self.miss}", 
                                           True, WHITE)
            info3_box = info3_text.get_rect()
            info3_box.centerx = self.window.centerx
            info3_box.top = info2_box.bottom

            info4_font = pygame.font.Font('freesansbold.ttf', 36)
            info4_text = info4_font.render(f"300: {self.hit300}", 
                                           True, WHITE)
            info4_box = info4_text.get_rect()
            info4_box.centerx = self.window.centerx
            info4_box.top = info3_box.bottom

            info5_font = pygame.font.Font('freesansbold.ttf', 36)
            info5_text = info5_font.render(f"100: {self.hit100}", 
                                           True, WHITE)
            info5_box = info5_text.get_rect()
            info5_box.centerx = self.window.centerx
            info5_box.top = info4_box.bottom

            
            info6_font = pygame.font.Font('freesansbold.ttf', 36)
            info6_text = info6_font.render(f"50: {self.hit50}", 
                                           True, WHITE)
            info6_box = info6_text.get_rect()
            info6_box.centerx = self.window.centerx
            info6_box.top = info5_box.bottom

            info7_font = pygame.font.Font('freesansbold.ttf', 36)
            info7_text = info7_font.render(f"Total Score: {self.score}", 
                                           True, WHITE)
            info7_box = info7_text.get_rect()
            info7_box.centerx = self.window.centerx
            info7_box.top = info6_box.bottom

            self.screen.blit(text_text, text_box)
            self.screen.blit(info1_text, info1_box)
            self.screen.blit(info2_text, info2_box)
            self.screen.blit(info3_text, info3_box)
            self.screen.blit(info4_text, info4_box)
            self.screen.blit(info5_text, info5_box)
            self.screen.blit(info6_text, info6_box)
            self.screen.blit(info7_text, info7_box)
            self.cursor.update(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.reset_vars()
                        self.gameState.set_state("LevelSelection")
                        paused = False
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.flip()

    def pause(self):
        '''
        Method for pausing the game and displaying the pause screen.
        '''

        BLACK = pygame.Color("Black")
        WHITE = pygame.Color("White")
        PAUSE_ALPHA = 100
        CURSOR_POS_COLOR = pygame.Color("Orange")
        CURSOR_RAD = self.cursor.cursor_img.get_height() / 2
        ORIGIN = (0, 0)

        pygame.mixer.music.pause()
        
        paused = True
        while paused:
            self.screen.fill(BLACK)
            self.backRow.blit(self.frontRow, ORIGIN)
            self.backRow.set_alpha(PAUSE_ALPHA)
            self.backRow.blit(self.screen, ORIGIN)
            text_font = pygame.font.Font('freesansbold.ttf', 64)
            text_text = text_font.render(f"PAUSED", True, WHITE)
            text_box = text_text.get_rect()
            text_box.centerx = self.window.centerx
            text_box.top = self.window.top
            info1_font = pygame.font.Font('freesansbold.ttf', 48)
            info1_text = info1_font.render(f"Click on circle to continue",
                                            True, WHITE)
            info1_box = info1_text.get_rect()
            info1_box.centerx = self.window.centerx
            info1_box.top = text_box.bottom
            info2_font = pygame.font.Font('freesansbold.ttf', 48)
            info2_text = info2_font.render(f"Press ESC to quit", 
                                           True, WHITE)
            info2_box = info2_text.get_rect()
            info2_box.centerx = self.window.centerx
            info2_box.top = info1_box.bottom

            self.screen.blit(text_text, text_box)
            self.screen.blit(info1_text, info1_box)
            self.screen.blit(info2_text, info2_box)
            circle = pygame.draw.circle(
                self.screen, CURSOR_POS_COLOR, self.mousePos, CURSOR_RAD)
            self.cursor.update(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.reset_vars()
                        self.gameState.set_state("LevelSelection")
                        self.quitGame = True
                        paused = False
                    if event.key in self.controls.values():
                        collision = circle.collidepoint(self.mousePos)
                        if collision:
                            pygame.mixer.music.unpause()
                            paused = False
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.flip()
    
    def score_lookup(self) -> bool:
        '''
        This method manages the score by calling
        the hit evaluation method as well as modifying the score
        '''

        scored = self.eval_hits()
        if scored == -1: 
            return True
        
        if self.comboBreak:
            if self.combo > self.comboBreakTreshold:
                self.soundChannel2.play(
                    self.sounds['combobreak'])
            self.combo = 1
        else:
            self.combo += 1
        self.score += scored * self.combo
        return False
    
    def get_inputs(self):
        '''
        Gets the inputs the user has entered and calls
        score managing method.
        '''

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.mousePos = pygame.mouse.get_pos()
                    self.pause()
                if event.key == self.controls["INPUT_KEY_1"]:
                    if self.clicked["INPUT_KEY_1"] == False:
                        self.clickTime = pygame.mixer.music.get_pos()
                        self.clicked["INPUT_KEY_1"] = True
                        if self.score_lookup():
                            continue
                if event.key == self.controls["INPUT_KEY_2"]:
                    if self.clicked["INPUT_KEY_2"] == False:
                        self.clickTime = pygame.mixer.music.get_pos()
                        self.clicked["INPUT_KEY_2"] = True
                        if self.score_lookup():
                            continue
            if event.type == pygame.KEYUP:
                if event.key == self.controls["INPUT_KEY_1"]:
                    self.clicked["INPUT_KEY_1"] = False
                if event.key == self.controls["INPUT_KEY_2"]:
                    self.clicked["INPUT_KEY_2"] = False

    def eval_slider_end(self, hit) -> int:
        '''
        Evaluates the score at the end of the slider.
        '''

        self.soundChannel.play(self.sounds['hitnormal'])
        pos = pygame.mouse.get_pos()
        collision = hit.hitbox.collidepoint(pos)
        if collision and not hit.sliderBreak and hit.sliderClicked \
            and (self.clicked['INPUT_KEY_1'] 
                 or self.clicked['INPUT_KEY_2']):
            self.combo += 1
            self.all += 3
            self.hit300 += 1
            self.create_score_obj(300, hit.hitbox.center)
            self.soundChannel.play(self.sounds['hitnormal'])
            self.hitQueue.remove(hit)
            return 300
        if collision and hit.sliderOut and hit.sliderClicked \
            and (self.clicked['INPUT_KEY_1'] 
                 or self.clicked['INPUT_KEY_2']):
            self.combo += 1
            self.all += 3
            self.hit100 += 1
            self.create_score_obj(100, hit.hitbox.center)
            self.soundChannel.play(self.sounds['hitnormal'])
            self.hitQueue.remove(hit)
            return 100
        if not collision and not hit.sliderOut and hit.sliderClicked \
            and (self.clicked['INPUT_KEY_1'] 
                    or self.clicked['INPUT_KEY_2']):
            self.combo += 1
            self.all += 3
            self.hit100 += 1
            self.create_score_obj(100, hit.hitbox.center)
            self.soundChannel.play(self.sounds['hitnormal'])
            self.hitQueue.remove(hit)
            return 100
        if collision and hit.sliderBreak and hit.sliderClicked \
             and (self.clicked['INPUT_KEY_1'] 
                 or self.clicked['INPUT_KEY_2']):
            self.combo += 1
            self.all += 3
            self.hit100 += 1
            self.create_score_obj(50, hit.hitbox.center)
            self.soundChannel.play(self.sounds['hitnormal'])
            self.hitQueue.remove(hit)
            return 50
        if not collision and not hit.sliderBreak and hit.sliderClicked \
             and (self.clicked['INPUT_KEY_1'] 
                 or self.clicked['INPUT_KEY_2']):
            self.combo += 1
            self.all += 3
            self.hit100 += 1
            self.create_score_obj(50, hit.hitbox.center)
            self.soundChannel.play(self.sounds['hitnormal'])
            self.hitQueue.remove(hit)
            return 50
        self.create_score_obj(0, hit.hitbox.center)
        if self.combo > self.comboBreakTreshold:
            self.soundChannel.play(self.sounds['combobreak'])
        self.hitQueue.remove(hit)
        self.comboBreak = True
        self.combo = 1
        self.all += 3
        self.miss += 1
        return 0

    def create_score_obj(self, value, position):
        '''
        Creates a score confirmation object to be displayed
        on the screen and adds it to the queue.
        '''
        
        img = self.scoreImages[value]
        img_box = img.get_rect()
        img_box.center = position        
        self.scoreQueue.append(
            ScoreObject(img, img_box, pygame.mixer.music.get_pos()))


    def eval_hits(self) -> int:
        '''
        Hit evaluation method. Checks whether the user clicked
        at the right time and on a right circle.
        '''

        self.musicTime = pygame.mixer.music.get_pos()
        cursorPos = pygame.mouse.get_pos()
        if len(self.hitQueue) < 1:
            return -1
        hit = self.hitQueue[0]
        collision = hit.hitbox.collidepoint(cursorPos)

        if collision:
            if hit.type['HITCIRCLE'] is True:

                if self.musicTime < hit.hitTime - hit.hitWindow['50']:
                    self.comboBreak = True
                    self.soundChannel.play(self.sounds['hitnormal'])
                    self.all += 3
                    self.miss += 1
                    self.create_score_obj(0, hit.hitbox.center)
                    self.hitQueue.pop(0)
                    return 0
                if self.musicTime > hit.hitTime - hit.hitWindow['50'] \
                    and self.musicTime < hit.hitTime - hit.hitWindow['100']:
                    self.comboBreak = False
                    self.soundChannel.play(self.sounds['hitnormal'])
                    self.all += 3
                    self.hit50 += 1
                    self.create_score_obj(50, hit.hitbox.center)
                    self.hitQueue.pop(0)
                    return 50
                if self.musicTime > hit.hitTime - hit.hitWindow['100'] \
                    and self.musicTime < hit.hitTime - hit.hitWindow['300']:
                    self.comboBreak = False
                    self.soundChannel.play(self.sounds['hitnormal'])
                    self.all += 3
                    self.hit100 += 1
                    self.create_score_obj(100, hit.hitbox.center)
                    self.hitQueue.pop(0)
                    return 100
                if self.musicTime > hit.hitTime - hit.hitWindow['300'] \
                    and self.musicTime < hit.hitTime + hit.hitWindow['300']:
                    self.comboBreak = False
                    self.soundChannel.play(self.sounds['hitnormal'])
                    self.all += 3
                    self.hit300 += 1
                    self.create_score_obj(300, hit.hitbox.center)
                    self.hitQueue.pop(0)
                    return 300
                if self.musicTime > hit.hitTime + hit.hitWindow['300'] \
                    and self.musicTime < hit.hitTime + hit.hitWindow['100']:
                    self.comboBreak = False
                    self.soundChannel.play(self.sounds['hitnormal'])
                    self.all += 3
                    self.hit100 += 1
                    self.create_score_obj(100, hit.hitbox.center)
                    self.hitQueue.pop(0)
                    return 100
                if self.musicTime > hit.hitTime + hit.hitWindow['100'] \
                    and self.musicTime < hit.hitTime + hit.hitWindow['50']:
                    self.comboBreak = False
                    self.hitQueue.pop(0)
                    self.soundChannel.play(self.sounds['hitnormal'])
                    self.all += 3
                    self.hit50 += 1
                    self.create_score_obj(50, hit.hitbox.center)
                    return 50
                if self.musicTime > hit.hitTime + hit.hitWindow['50']:
                    self.comboBreak = True
                    self.soundChannel.play(self.sounds['hitnormal'])
                    self.all += 3
                    self.miss += 1
                    self.create_score_obj(0, hit.hitbox.center)
                    self.hitQueue.pop(0)
                    return 0
                
            if hit.type['SLIDER'] is True:
                if self.musicTime < hit.hitTime - hit.hitWindow['50']:
                    self.comboBreak = True
                    hit.sliderBreak = True
                    return 0
                if self.musicTime > hit.hitTime - hit.hitWindow['50'] \
                    and self.musicTime < hit.hitTime + hit.hitWindow['50']:
                    self.comboBreak = False
                    if hit.sliderClicked is False:
                        self.soundChannel.play(self.sounds['hitnormal'])
                    hit.sliderClicked = True
                    return -1
                if self.musicTime > hit.hitTime + hit.hitWindow['50']:
                    self.comboBreak = True
                    hit.sliderBreak = True
                    return 0
        return -1
