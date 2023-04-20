from module import Module
from scene import Scene

import pygame

class Score(Module):
    def __init__(self, screen: pygame.Surface, state: Scene) -> None:
        super().__init__(screen, state)

    def run(self):
        pass