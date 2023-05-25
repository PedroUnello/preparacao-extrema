from scene import Scene
from state import State
from menu import Menu
from game import Game
from score import Score

import pygame

def create():

    pygame.init()
    screen_size = (1600, 900)
    screen = pygame.display.set_mode(screen_size, 0, 32)

    clock = pygame.time.Clock()

    state = State()

    modules = {
        Scene.MENU  :   Menu(screen, state),
        Scene.GAME  :   Game(screen, state),
        Scene.SCORE :   Score(screen, state)
    }

    while True:

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        modules[ state.scene ].run(events, clock)

        pygame.display.update()

