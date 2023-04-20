from scene import Scene
from menu import Menu
from game import Game
from score import Score

import pygame


def create():

    pygame.init()
    screen_size = (1280, 720)
    screen = pygame.display.set_mode(screen_size, 0, 32)

    clock = pygame.time.Clock()

    state = Scene.GAME

    states = {
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

        states[state].run(events)

        clock.tick(  )

        pygame.display.update()

