class GameStateManager:
    def __init__(self, *, state="MainMenu"):
        self.state = state

    def get_state(self):
        return self.state

    def set_state(self, state):
        self.state = state
        return self.state
