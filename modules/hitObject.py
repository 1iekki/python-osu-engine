class HitObject:
   

    def __init__(self, description: str, difficulty: dict, beatLength: float):

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
        self.time = params[2]
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

        self.showTime = self.time - self.preempt
        self.hitbox = None
        self.curve = None

        if self.type['SLIDER']:
            match params[5][0]:
                case 'B':
                    self.sliderType = 'B' # bezier
                case 'C':
                    self.sliderType = 'C' # centripedal catmull-rom
                case 'L':
                    self.sliderType = 'L' # linear
                case 'P':
                    self.sliderType = 'P' # perfect circle
            for x in params[5][2:].split('|'):
                i = 0
                b = [0, 0]
                for y in x.split(':'):
                    b[i] = int(y)
                    i += 1
                self.sliderCurvePoints.append(b)
            # self.sliderCurvePoints = ([x.split(':') for x in params[5][2:].split('|')])
            
            self.slides = params[6]
            if type(params[7]) == int:
                self.sliderLength = params[7]
            else:
                self.sliderLength = int(float(params[7].strip()))

            SV = 1
            self.sliderTime = self.sliderLength / (int(difficulty['SliderMultiplier']) * 100 * SV) * beatLength

        OD = float(difficulty['OverallDifficulty'])
        self.hitWindow = {'300': int(80 - 6 * OD),
                          '100': int(140 - 8 * OD),
                          '50': int(200 - 10 * OD)
                          }

