import os

class HitObject:
   

    def __init__(self, description: str, difficulty: dict):

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
        self.sliderCurvePoints = []
        self.slides = 0
        self.sliderLength = 0
        
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
            self.sliderCurvePoints = ([x.split(':') for x in params[5][2:].split('|')])
            self.slides = params[6]
            if type(params[7]) == int:
                self.sliderLength = params[7]
            else:
                self.sliderLength = int(float(params[7].strip()))

        self.OD = float(difficulty['OverallDifficulty'])
        self.hitWindow = {'300': int(80 - 6 * self.OD),
                          '100': int(140 - 8 * self.OD),
                          '50': int(200 - 10 * self.OD)
                          }

class Beatmap:
    def __init__(self, dir: str, name: str):

        # constants
        CIRCLE_SIZE = 55
        CIRCLE_SCALE = 4

        self.dir = dir
        self.name = name
        with open(f"{dir}/{name}", mode = 'r', encoding='utf_8') as file:
            try:
                lines = file.readlines()
                self.generalData = self.get_data("[General]\n", lines)
                self.metadata = self.get_data("[Metadata]\n", lines)
                self.difficulty = self.get_data("[Difficulty]\n", lines)
            except:
                pass    
        CS = float(self.difficulty['CircleSize'])
        self.circleSize = CIRCLE_SIZE - CIRCLE_SCALE * CS

    def get_data(self, what: str, where: list) -> dict:
        d ={}
        id = where.index(what)
        end = where.index("\n", id)
        for x in where[id+1:end]:
            div = x.index(":")
            d[x[:div].strip()] = x[div+1:-1].strip()
        return d

    def get_hitobjects(self) -> list:
        hit = []
        with open(f"{self.dir}/{self.name}", mode='r', encoding='utf_8') as file:
            lines = file.readlines()
            id = lines.index("[HitObjects]\n")
            for desc in lines[id+1:]:
                hit.append(HitObject(desc, self.difficulty))
        return hit
    
    def get_audio(self) -> str:
        return f"{self.dir}/{self.generalData['AudioFilename']}"

    def __repr__(self) -> str:
        return self.name


def search(dir : str) -> list:
    beatmaps = []
    for map in os.listdir(dir):
        for file in os.listdir(f"{dir}/{map}"):
            if file.endswith(".osu"):
                beatmaps.append(Beatmap(f"{dir}/{map}", file))
    return beatmaps

def main():
    maps = search("beatmaps")
    for map in maps:
        map.get_hitobjects()

if __name__ == "__main__":
    main()