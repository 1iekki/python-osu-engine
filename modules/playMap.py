import pygame
import sys
import math
from modules.gameStateManager import GameStateManager
from modules.cursor import Cursor
from modules.beatmap_parser import Beatmap


class PlayMap:
   
    def __init__(self, screen: pygame.Surface,
                 gameState: GameStateManager, 
                 clock: pygame.time.Clock,
                 settings: dict,
                 cursor: Cursor):
        
        BACKROW_ALPHA = 160
        COMBOBREAK_THRESHOLD = 5

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
        self.sounds = {
            'hitnormal': pygame.mixer.Sound("hitsounds/normal-hitnormal.wav"),
            'slidertick': pygame.mixer.Sound("hitsounds/normal-slidertick.wav"),
            'combobreak': pygame.mixer.Sound("hitsounds/combobreak.mp3")}
        self.soundChannel.set_volume(0.3)
        self.frontRow = self.screen.copy()
        self.backRow = self.screen.copy()
        self.backRow.convert_alpha()
        self.backRow.set_alpha(BACKROW_ALPHA)
        self.sliderColor = (95, 95, 95)
        self.sliderCircleWidth = 2
        self.sliderCircleColor = (255, 255, 255)
        self.hitNum = 1

    def set_map(self, map: Beatmap):
        
        SLIDER_BALL_SCALE = 1.5

        self.map = map
        self.hitObjects = map.get_hitobjects()
        self.music = map.get_audio()
        
        size = self.map.circleSize * self.scale_factor * 2
        self.circleSize = (size, size)     

        self.sliderBallSize = (size * SLIDER_BALL_SCALE,
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

    def run(self):

        #init sliders
        for hit in self.hitObjects:
            if hit.type['SLIDER'] is True:
                hit.generate_slider_path(self.scale_factor, self.pos_x, self.pos_y)

        pygame.draw.rect(self.screen, (255,255,255), ((self.pos_x, self.pos_y), (self.playField)))
        pygame.mixer.music.load(self.music)
        pygame.mixer.music.play()
        pygame.mixer.music.set_pos(0)
        pygame.mixer.music.set_volume(0.1)
        while pygame.mixer.music.get_busy():
            self.render_hitobjects()
            self.get_inputs()
            self.show_score()
            self.cursor.update(self.frontRow)
            self.screen.blit(self.frontRow, (0,0))
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
        
        self.frontRow.blit(score_text, score_box)
        self.frontRow.blit(combo_text, combo_box)
        self.frontRow.blit(acc_text, acc_box)

    def render_hitobjects(self):
        
        SLIDER_END = 0
        SLIDER_BOUNCES = 2
        SLIDER_ADVANCES = 1

        if self.rendered < len(self.hitObjects):
            hitTime = self.hitObjects[self.rendered].showTime
            musicTime = pygame.mixer.music.get_pos()
            if hitTime <= musicTime:         
                self.hitQueue.append(self.hitObjects[self.rendered])
                self.rendered += 1

        self.screen.fill(pygame.Color("Black"))
        empty = pygame.Color(0,0,0,0)
        self.frontRow.fill(empty)
        self.frontRow.blit(self.backRow, (0, 0))
        self.backRow.fill(empty)

        queue = self.hitQueue.copy()
        queue.reverse()
        for i, hit in enumerate(queue):
            if hit.hitnum == 0:
                if hit.type['NEWCOMBO'] is True:
                    self.hitNum = 1
                else:
                    self.hitNum += 1
                if self.hitNum > 9:
                    self.hitNum = 1
                hit.hitnum = self.hitNum

            if i == queue.index(queue[-1]):
                surf = self.frontRow
            else:
                surf = self.backRow

            musicTime = pygame.mixer.music.get_pos()
            if hit.type ['HITCIRCLE'] is True:

                if musicTime >= hit.showTime + hit.preempt + hit.hitWindow['50']:
                    self.hitQueue.remove(hit)
                    self.miss += 1
                    self.all += 3
                    if self.combo > self.comboBreakTreshold:
                        self.soundChannel2.play(self.sounds['combobreak'])
                    self.combo = 1
                    continue 

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
                hitnum = pygame.transform.smoothscale(self.hitInternal[hit.hitnum], self.circleSize)
                hitnum.convert_alpha()
                hitnum.set_alpha(opacity)
                hitnum_box = img.get_rect()
                hitnum_box.center = (x, y)
                surf.blit(hitnum, hitnum_box)
                surf.blit(img, img_box)
                surf.blit(ac, ac_box)
                hit.hitbox = img_box

            
            if hit.type['SLIDER'] is True:

                # draw slider outline
                path = hit.get_slider_path()
                radius = self.circleSize[0] / 2
                for (x,y) in path:
                    pygame.draw.circle(surf, self.sliderColor, (x,y), radius)
                pygame.draw.circle(surf, self.sliderCircleColor, path[0], radius, self.sliderCircleWidth)
                pygame.draw.circle(surf, self.sliderCircleColor, path[-1], radius, self.sliderCircleWidth)
                if hit.slides > 1:
                    bounce_img = pygame.transform.smoothscale(self.sliderBounceIMG, self.circleSize)
                    bounce_box = bounce_img.get_rect()
                    bounce_box.center = path[-1]
                    surf.blit(bounce_img, bounce_box)

                #slider activation
                if musicTime >= hit.hitTime:
                    hit.sliderRuns = True

                #slider movement                
                if hit.sliderRuns is True:
                    relTime = musicTime - hit.hitTime
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
                    img = pygame.transform.smoothscale(self.hitCircleIMG, self.circleSize)
                    img.convert_alpha()
                    img_box = img.get_rect()
                    img_box.center = (new_x, new_y)
                    ac = pygame.transform.smoothscale(self.approachCircle, self.sliderBallSize)
                    ac_box = ac.get_rect()
                    ac_box.center = (new_x, new_y)
                    surf.blit(ac, ac_box)
                    surf.blit(img, img_box)
                    hit.hitbox = ac_box

                    pos = pygame.mouse.get_pos()
                    collision = hit.hitbox.collidepoint(pos)
                    if not collision:
                        hit.sliderOut = True
                    tick = hit.sliderTick
                    if relTime - tick * hit.ticks >= tick:
                        hit.ticks += 1
                        if not collision:
                            self.comboBreak = True
                            hit.sliderBreak = True
                        else:
                            self.combo += 1
                else:
                    x = hit.x * self.scale_factor
                    y = hit.y * self.scale_factor
                    x += self.pos_x
                    y += self.pos_y
                    x = int(x)
                    y = int(y)

                    relTime = musicTime - hit.showTime
                    fadeIN = relTime/float(hit.fadeIn)

                    opacity = 255 if fadeIN > 1.0 else int(255*fadeIN)          

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
                    surf.blit(hitnum, hitnum_box)
                    surf.blit(img, img_box)
                    surf.blit(ac, ac_box)
                    hit.hitbox = img_box
                    pygame.draw.lines(self.screen, pygame.Color("White"),
                                      False, hit.get_slider_path())
                    
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
                            if self.combo > self.comboBreakTreshold:
                                self.soundChannel2.play(self.sounds['combobreak'])
                            self.combo = 1
                        else:
                            self.combo += 1
                        self.score += scored * self.combo
                if event.key == self.controls["INPUT_KEY_2"]:
                    if self.clicked["INPUT_KEY_2"] == False:
                        self.clickTime = pygame.mixer.music.get_pos()
                        self.clicked["INPUT_KEY_2"] = True
                        scored = self.eval_hits()
                        if scored == -1: continue
                        if scored == 0:
                            if self.combo > self.comboBreakTreshold:
                                self.soundChannel2.play(self.sounds['combobreak'])
                            self.combo = 1
                        self.score += scored * self.combo
            if event.type == pygame.KEYUP:
                if event.key == self.controls["INPUT_KEY_1"]:
                    self.clicked["INPUT_KEY_1"] = False
                if event.key == self.controls["INPUT_KEY_2"]:
                    self.clicked["INPUT_KEY_2"] = False

    def eval_slider_end(self, hit) -> int:
        self.soundChannel.play(self.sounds['hitnormal'])
        pos = pygame.mouse.get_pos()
        collision = hit.hitbox.collidepoint(pos)
        if collision and not hit.sliderOut \
            and (self.clicked['INPUT_KEY_1'] \
                 or self.clicked['INPUT_KEY_2']):
            self.combo += 1
            self.hitQueue.remove(hit)
            self.all += 3
            self.hit300 += 1
            return 300
        if collision and hit.sliderOut \
            and (self.clicked['INPUT_KEY_1'] \
                 or self.clicked['INPUT_KEY_2']):
            self.combo += 1
            self.all += 3
            self.hit100 += 1
            self.hitQueue.remove(hit)
            return 100
        if collision and hit.sliderBreak \
            and (self.clicked['INPUT_KEY_1'] \
                 or self.clicked['INPUT_KEY_2']):
            self.all += 3
            self.hit50 += 1
            self.hitQueue.remove(hit)
            return 50
        self.hitQueue.remove(hit)
        self.comboBreak = True
        self.all += 3
        self.miss += 1
        return 0

    def eval_hits(self) -> int:
        musicTime = pygame.mixer.music.get_pos()
        cursorPos = pygame.mouse.get_pos()
        if len(self.hitQueue) < 1:
            return -1
        hit = self.hitQueue[0]
        collision = hit.hitbox.collidepoint(cursorPos)

        if collision:
            if hit.type['HITCIRCLE'] == True:

                if musicTime < hit.hitTime - hit.hitWindow['50']:
                    self.comboBreak = True
                    self.hitQueue.pop(0)
                    self.soundChannel.play(self.sounds['hitnormal'])
                    self.all += 3
                    self.miss += 1
                    return 0
                if musicTime > hit.hitTime - hit.hitWindow['50'] \
                    and musicTime < hit.hitTime - hit.hitWindow['100']:
                    self.comboBreak = False
                    self.hitQueue.pop(0)
                    self.soundChannel.play(self.sounds['hitnormal'])
                    self.all += 3
                    self.hit50 += 1
                    return 50
                if musicTime > hit.hitTime - hit.hitWindow['100'] \
                    and musicTime < hit.hitTime - hit.hitWindow['300']:
                    self.comboBreak = False
                    self.hitQueue.pop(0)
                    self.soundChannel.play(self.sounds['hitnormal'])
                    self.all += 3
                    self.hit100 += 1
                    return 100
                if musicTime > hit.hitTime - hit.hitWindow['300'] \
                    and musicTime < hit.hitTime + hit.hitWindow['300']:
                    self.comboBreak = False
                    self.hitQueue.pop(0)
                    self.soundChannel.play(self.sounds['hitnormal'])
                    self.all += 3
                    self.hit300 += 1
                    return 300
                if musicTime > hit.hitTime + hit.hitWindow['300'] \
                    and musicTime < hit.hitTime + hit.hitWindow['100']:
                    self.comboBreak = False
                    self.hitQueue.pop(0)
                    self.soundChannel.play(self.sounds['hitnormal'])
                    self.all += 3
                    self.hit100 += 1
                    return 100
                if musicTime > hit.hitTime + hit.hitWindow['100'] \
                    and musicTime < hit.hitTime + hit.hitWindow['50']:
                    self.comboBreak = False
                    self.hitQueue.pop(0)
                    self.soundChannel.play(self.sounds['hitnormal'])
                    self.all += 3
                    self.hit50 += 1
                    return 50
                if musicTime > hit.hitTime + hit.hitWindow['50']:
                    self.comboBreak = True
                    self.hitQueue.pop(0)
                    self.soundChannel.play(self.sounds['hitnormal'])
                    self.all += 3
                    self.miss += 1
                    return 0
                
            if hit.type['SLIDER'] == True:
                if musicTime < hit.hitTime - hit.hitWindow['50']:
                    self.comboBreak = True
                    
                    return 0
                if musicTime > hit.hitTime - hit.hitWindow['50'] \
                    and musicTime < hit.hitTime - hit.hitWindow['300']:
                    self.comboBreak = False
                    if hit.sliderClicked is False:
                        self.soundChannel.play(self.sounds['hitnormal'])
                    hit.sliderClicked = True
                    return -1
                if musicTime > hit.hitTime - hit.hitWindow['300'] \
                    and musicTime < hit.hitTime + hit.hitWindow['300']:
                    self.comboBreak = False
                    if hit.sliderClicked is False:
                        self.soundChannel.play(self.sounds['hitnormal'])
                    hit.sliderClicked = True
                    return -1
                if musicTime > hit.hitTime + hit.hitWindow['300'] \
                    and musicTime < hit.hitTime + hit.hitWindow['50']:
                    self.comboBreak = False
                    if hit.sliderClicked is False:
                        self.soundChannel.play(self.sounds['hitnormal'])
                    hit.sliderClicked = True
                    return -1
                if musicTime > hit.hitTime + hit.hitWindow['50']:
                    self.comboBreak = True
                    self.soundChannel2.play(self.sounds['hitnormal'])
                    return 0
        return -1
