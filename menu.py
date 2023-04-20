from module import Module
from module import Module
from module import Module
from scene import Scene

import pygame
import pygame_menu
import os

class Menu(Module):
    
    def __init__(self, screen: pygame.Surface, state: Scene) -> None:
        super().__init__(screen, state)

        self.__handle = pygame_menu.Menu('Preparação Extrema', screen.get_rect().width, screen.get_rect().height, theme=pygame_menu.themes.THEME_SOLARIZED)

        cenarios = [os.path.splitext(nome)[0] for nome in os.listdir("./cenarios")]
        cenarios = [(j, i) for i,j in enumerate(cenarios)]

        self.__handle.add.text_input('Nome :', default='LEANDRO PUPO NATALE')
        self.__handle.add.button('Jogar')
        self.__handle.add.selector('Cenarios :', cenarios)
        self.__handle.add.selector('Dificuldade :', [('Hard', 1), ('Medium', 2), ('Easy', 3)])
        self.__handle.add.button('Sair', pygame_menu.events.EXIT)

    def run(self):
        self.__handle.mainloop(self.screen)



