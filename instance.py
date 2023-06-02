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

    last_scene = Scene.MENU

    while True:

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        #On switch scenes, recreate instance.
        if last_scene != state.scene:
            match state.scene:
                case Scene.MENU:
                    modules[ Scene.MENU ] = Menu(screen, state)
                case Scene.GAME:
                    modules[ Scene.GAME ] = Game(screen, state)
                case Scene.SCORE:
                    modules[ Scene.SCORE ] = Score(screen, state)
            last_scene = state.scene

        modules[ state.scene ].run(events, clock)

        pygame.display.update()

