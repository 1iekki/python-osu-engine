import pickle
import pygame

SETUP = {"SCREEN_RESOLUTION": (1280, 720),
             "SCREEN_FLAGS": pygame.SHOWN,
             "FPS_CAP": 60,
             "PLAYFIELD_DIMENSIONS": (640,480),
             "COLOR_DEPTH": 32
            }

if __name__ == "__main__":
    file = open("bin/setup.pkl", "wb")
    pickle.dump(SETUP, file)
    file.close()