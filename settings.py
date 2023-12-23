import pickle
import pygame

if __name__ == "__main__":
    SETUP = {"SCREEN_RESOLUTION": (1280, 720),
             "SCREEN_FLAGS": pygame.SHOWN,
             "FPS_CAP": 60
            }

    file = open("bin/setup.pkl", "wb")
    pickle.dump(SETUP, file)
    file.close()