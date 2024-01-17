import pickle
import pygame

SETUP = {"SCREEN_RESOLUTION": (1280, 720),
             "SCREEN_FLAGS": pygame.SHOWN,
             "FPS_CAP": 999,
             "PLAYFIELD_DIMENSIONS": (640,480),
             "PLAYFIELD_MARGIN": 60,
             "INPUT_KEY_1": pygame.K_s,
             "INPUT_KEY_2": pygame.K_d,
             'SCREEN_DEPTH': 32,
             "MUSIC_VOLUME": 0.1,
             "SOUND_VOLUME": 0.1
            }

if __name__ == "__main__":
    file = open("bin/setup.pkl", "wb")
    pickle.dump(SETUP, file)
    file.close()