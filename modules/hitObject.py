from modules.curves import Curve
class HitObject:
   

    def __init__(self, description: str, difficulty: dict, timingPoints: list):

        # constants
        PREEMPT = 1200
        LOW_AR_PREEMPT = 600
        HIGH_AR_PREEMPT = 750
        FADE_IN = 800
        LOW_AR_FADE = 400
        HIGH_AR_FADE = 500
        
        params = [int(e) if e.isdigit() else e for e in description.split(',')]
        self.x = params[0]
        self.y = params[1]
        self.hitTime = int(params[2])
        t = format(params[3], '#07b')
        self.type = {'HITCIRCLE': bool(int(t[-1])),
                     'SLIDER': bool(int(t[-2])),
                     'NEWCOMBO': bool(int(t[-3])),
                     'SPINNER': bool(int(t[-4]))
                     }
        self.sliderType = 'N' # not a slider
        self.sliderCurvePoints = [[self.x,self.y]]
        self.slides = 0
        self.sliderLength = 0
        self.sliderTime = 0
        self.sliderRuns = False
        
        AR = float(difficulty["ApproachRate"])
        if AR < 5:
            self.preempt = int(PREEMPT + (LOW_AR_PREEMPT * (5 - AR) / 5))
            self.fadeIn = int(FADE_IN + (LOW_AR_FADE * (5 - AR) / 5))
        elif AR == 5:
            self.preempt = int(PREEMPT)
            self.fadeIn = int(FADE_IN)
        elif AR > 5:
            self.preempt = int(PREEMPT - (HIGH_AR_PREEMPT * (AR - 5) / 5))
            self.fadeIn = int(FADE_IN - (HIGH_AR_FADE * (AR - 5) / 5))

        self.showTime = self.hitTime - self.preempt
        self.hitbox = None
        self.curve = None
        self.curvePath = None
        self.curvePointer = 0
        self.curvePathCount = 0
        self.beatLength = 0
        self.SV = 0
        self.slidesPerformed = 0
        self.sliderTick = 0
        self.hitnum = 0
        self.sliderClicked = False


        if self.type['SLIDER']:
            for x in params[5][2:].split('|'):
                i = 0
                b = [0, 0]
                for y in x.split(':'):
                    b[i] = int(y)
                    i += 1
                self.sliderCurvePoints.append(b)
            match params[5][0]:
                case 'B':
                    self.sliderType = 'B' # bezier
                case 'C':
                    self.sliderType = 'C' # centripedal catmull-rom
                case 'L':
                    self.sliderType = 'L' # linear
                case 'P':
                    self.sliderType = 'P' # perfect circle
            self.slides = params[6]
            if type(params[7]) == int:
                self.sliderLength = params[7]
            else:
                self.sliderLength = int(float(params[7].strip()))
            timingPtr = timingPoints.index(timingPoints[-1])
            timingReferencePtr = timingPoints.index(timingPoints[-1])
            for id, point in enumerate(timingPoints[:-2]):
                if self.hitTime > point[0]:
                    continue
                if self.hitTime <= timingPoints[id + 1][0]:
                    timingPtr = id
                    if point[1] > 0:
                        timingReferencePtr = timingPtr
                    else:
                        i = len(timingPoints[:timingPtr]) - 1
                        while timingPoints[i][1] < 0:
                            i -= 1
                        timingReferencePtr = i
                    break
            self.beatLength = timingPoints[timingReferencePtr][1]
            if timingPtr == timingReferencePtr:
                self.SV = 1
            else:
                self.SV = (100/abs(float(timingPoints[timingPtr][1])))
            self.sliderTime = self.sliderLength / (int(difficulty['SliderMultiplier']) * 100 * self.SV) * self.beatLength
            self.sliderTick =  self.beatLength / float(difficulty['SliderTickRate'])
            self.sliderBreak = False
            self.sliderOut = False
            self.ticks = 0
            self.sliderClicked = False
            
        OD = float(difficulty['OverallDifficulty'])
        self.hitWindow = {'300': int(80 - 6 * OD),
                          '100': int(140 - 8 * OD),
                          '50': int(200 - 10 * OD)
                          }

    def get_slider_path(self) -> list:
        return self.curvePath

    def generate_slider_path(self, scale_factor, posx, posy):
        self.curve = Curve(self.sliderCurvePoints)
        self.curvePath = self.curve.get_bezier_path(scale_factor, posx, posy)
        self.curvePathCount = len(self.curvePath)

    def advance_slider(self, Time) -> bool:
        
        Time -= self.sliderTime * (self.slidesPerformed)

        if self.type["SLIDER"] is False:
            return -1 # NOT A SLIDER
        next_point = int((Time / self.sliderTime) *  self.curvePathCount)
        if next_point + 1 >= self.curvePathCount:
            self.slides -= 1
            if self.slides > 0:
                self.slidesPerformed += 1
                self.curvePath.reverse()
                self.curvePointer = 0
                return 2 # OK, SLIDER BOUNCES
            else:
                self.curvePointer = self.curvePathCount - 1
                return 0 # END OF SLIDER
        self.curvePointer = next_point
        return 1 # OK

    def get_slider_phase(self) -> list:
        return self.curvePath[self.curvePointer]


