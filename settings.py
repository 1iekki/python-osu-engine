import pickle
import pygame

SETUP = {"SCREEN_RESOLUTION": (1920, 1080),
             "SCREEN_FLAGS": pygame.FULLSCREEN,
             "FPS_CAP": 60,
             "PLAYFIELD_DIMENSIONS": (640,480),
             "PLAYFIELD_MARGIN": 60
            }

if __name__ == "__main__":
    file = open("bin/setup.pkl", "wb")
    pickle.dump(SETUP, file)
    file.close()