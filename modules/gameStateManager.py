'''
Module containing the game state manager, which controls
which panel is currently displayed.
'''

class GameStateManager:
    def __init__(self, *, state="MainMenu"):
        self.state = state

    def get_state(self) -> str:
        '''
        Returns the current gamestate
        '''
        return self.state

    def set_state(self, state):
        '''
        Sets the current game state
        '''
        self.state = state
