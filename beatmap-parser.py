from typing import Any, TextIO
import os
import pygame

class Beatmap:
    def __init__(self, dir: str):
        self.dir = dir
        with open(dir) as file:
            lines = file.readlines()
            self.metadata = self.parser_find("[Metadata]\n", lines)

    def parser_find(self, what: str, where: list) -> dict:
        d ={}
        id = where.index(what)
        end = where.index("\n", id)
        for x in where[id+1:end]:
            div = x.index(":")
            d[x[:div]] = x[div+1:-1]
        return d
    
    def __repr__(self) -> str:
        return self.dir


def search(dir : str) -> list:
    beatmaps = []
    for map in os.listdir(dir):
        for file in os.listdir(f"{dir}/{map}"):
            if file.endswith(".osu"):
                beatmaps.append(Beatmap(f"{dir}/{map}/{file}"))
    return beatmaps

def main():
    maps = search("beatmaps")

if __name__ == "__main__":
    main()