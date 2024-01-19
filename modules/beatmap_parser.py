'''
Module for parsing the beatmap file
'''

import os
from modules.beatmap import Beatmap

def search(dir : str) -> list:
    '''
    Search for maps in a directory,
    Returns a lits of maps
    '''
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