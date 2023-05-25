from module import Module
from scene import Scene
from state import State

import pygame
import pygame_menu
import os

class Menu(Module):
    
    def __init__(self, screen: pygame.Surface, state:State) -> None:
        super().__init__(screen, state)

        self.__handle = pygame_menu.Menu('Preparação Extrema', screen.get_rect().width, screen.get_rect().height, theme=pygame_menu.themes.THEME_SOLARIZED)

        cenarios = [os.path.splitext(nome)[0] for nome in os.listdir("./cenarios")]
        cenarios = [(j, i) for i,j in enumerate(cenarios)]

        default_name = 'Jogador 1'

        self.state.name = default_name
        self.state.cenario = cenarios[0][0]

        self.__handle.add.text_input('Nome: ', default=default_name, onchange=self.__set_name, maxchar=18)
        self.__handle.add.button('Jogar', self.__play)
        self.__handle.add.selector('Cenarios: ', cenarios, onchange=self.__set_cenario)
        self.__handle.add.selector('Difficuldade: ', [('Hard', 1), ('Medium', 2), ('Easy', 3)], onchange=self.__set_difficulty)
        self.__handle.add.button('Sair', pygame_menu.events.EXIT)

    def __play(self):
        #self.state = State()
        self.state.scene = Scene.GAME
        self.__handle.disable()

    def __set_name(self, value):
        self.state.name = value

    def __set_cenario(self, value, _):
        self.state.cenario = value[0][0]

    def __set_difficulty(self, value, _):
        self.state.difficulty = value

    def run(self, _, clock ):
        self.__handle.enable()
        self.__handle.mainloop(self.screen)
        



