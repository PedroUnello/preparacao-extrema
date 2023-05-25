from state import State
from abc import ABC, abstractmethod

import pygame

class Module(ABC):
    def __init__(self, screen:pygame.Surface, state:State) -> None:
        self.screen = screen
        self.state = state

    @abstractmethod
    def run(self, events:list[pygame.event.Event], clock:pygame.time.Clock):
        pass