import os

class HitObject:
    def __init__(self, objDef: str):
        params = [int(e) if e.isdigit() else e for e in objDef.split(',')]
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
        #params[5] is objectparams
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

class Beatmap:
    def __init__(self, dir: str, name: str):
        self.dir = dir
        self.name = name
        with open(f"{dir}/{name}") as file:
            lines = file.readlines()
            self.generalData = self.get_data("[General]\n", lines)
            self.metadata = self.get_data("[Metadata]\n", lines)

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
        with open(f"{self.dir}/{self.name}") as file:
            lines = file.readlines()
            id = lines.index("[HitObjects]\n")
            for x in lines[id+1:]:
                hit.append(HitObject(x))
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