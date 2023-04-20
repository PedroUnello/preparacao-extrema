from scene import Scene
from abc import ABC, abstractmethod

import pygame

class Module(ABC):
    def __init__(self, screen:pygame.Surface, state:Scene) -> None:
        self.screen = screen 

    @abstractmethod
    def run(self, events:list[pygame.event.Event]):
        pass