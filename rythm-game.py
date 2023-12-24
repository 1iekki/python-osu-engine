import pygame
import pickle
import sys

class GameStateManager:
    def __init__(self, *, state="MainMenu"):
        self.state = state

    def get_state(self):
        return self.state

    def set_state(self, state):
        self.state = state
        return self.state

class MainMenu:
    def __init__(self, screen: pygame.Surface, gameState: GameStateManager):
        self.screen = screen
        self.gameState = gameState

    def run(self):
        self.screen.fill(pygame.Color("Black"))
        
        self.controls()

    def controls(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

class LevelSelection(MainMenu):
    def run(self):
        self.screen.fill(pygame.Color("Blue"))
        self.controls()

    def controls(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_c:
                    self.gameState.set_state("MainMenu")

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        with open("bin/setup.pkl", "rb") as file:
            self.settings = pickle.load(file)

        self.screen = pygame.display.set_mode(
            self.settings["SCREEN_RESOLUTION"],
            self.settings["SCREEN_FLAGS"]
        )
        self.fpsCap = self.settings["FPS_CAP"]
        
        self.clock = pygame.time.Clock()
        self.gameState = GameStateManager()
        self.mainMenu = MainMenu(self.screen, self.gameState)
        self.levelSelection = LevelSelection(self.screen, self.gameState)

        self.STATES = {"MainMenu": self.mainMenu,
                       "LevelSelection": self.levelSelection 
                      }

    def run(self):

        while True:
            # dont place any code here, any changes should be made
            # in run methods of level objects specified in STATES

            currentState = self.STATES[self.gameState.get_state()]            
            currentState.run()
            pygame.display.flip()
            self.clock.tick(self.fpsCap)


def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()