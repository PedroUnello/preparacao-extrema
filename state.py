from scene import Scene
class State():
    def __init__(self) -> None:
        self.scene = Scene.MENU
        self.name = ""
        self.difficulty = 0
        self.cenario = ""
        self.score = 0

    def load_game(self, map):
        pass

    def get_scene(self) -> Scene:
        return self.__scene