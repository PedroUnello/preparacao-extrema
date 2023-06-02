from module import Module
from scene import Scene
from state import State
from utils import *

import pygame
import numpy as np

# Define as cores
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
VERDE = (0, 255, 0)
AMARELO = (255,255,0)
VERMELHO = (255, 0, 0)

class Score(Module):
    def __init__(self, screen: pygame.Surface, state: State) -> None:
        super().__init__(screen, state)
        
        #Insert in file player score (overwriting if same name already exists)
        found = False
        high_score_file = open("./score/score_board.txt", "w+")
        content = high_score_file.read()
        for line in content:
            re_line = line.replace("\n", "")
            values = re_line.split( ':' )
            name = values[0]
            if (name == state.name):
                line = str(state.name) + ':' + state.score
                found = True
                break

        if not found:
            high_score_file.writelines(str(state.name) + ':' + str(state.score))

        self.__progress = clamp( state.score, 0, 100 )
        self.__progress_colors = { 
            0:VERMELHO,
            50:AMARELO,
            100:VERDE
        }

        high_score_file.write(content)
        high_score_file.close()

    def run(self, events, clock):

        # draw in-text form of progress
        font = pygame.font.SysFont(None, 30)

        for event in events:
            if event.type == pygame.KEYDOWN: #Remove below
                if event.key == pygame.K_SPACE:
                    self.state.scene = Scene.MENU

        screen_unit = (self.screen.get_width() // 10, self.screen.get_height() // 10)
        bar_position = (screen_unit[0] * 2, screen_unit[1] * 7)
        bar_size = (screen_unit[0] * 6, screen_unit[1] // 3)
        full_bar = (self.__progress / 100) * (bar_size[0] - 2 * 2)

        if self.__progress not in self.__progress_colors:
            keys = np.array(list(self.__progress_colors))
            nearest_elem_ind = np.absolute( keys - self.__progress ).argmin() #Closest element (in value) to progress, returning its index
            nearest_elem = keys[nearest_elem_ind]
                                        #Get interval of progress
            interval_other_value = keys[nearest_elem_ind - 1 if self.__progress < nearest_elem else nearest_elem_ind + 1] #and the other value of this interval
            
            least_value = min(nearest_elem, interval_other_value)
            max_value = max(nearest_elem, interval_other_value)
            factor = ( self.__progress - least_value ) / (max_value - least_value) #Factor is percentage o reaching the next value in interval
            
            bar_color = tuple( #MOve to init after testing
                lerp(channel_val_1, channel_val_2, factor) #Lerp values in all channels
                for channel_val_1, channel_val_2 in zip( self.__progress_colors[least_value], self.__progress_colors[max_value] )
            )
        else:
            bar_color = self.__progress_colors[self.__progress]

        self.screen.fill(BRANCO)

        pygame.draw.rect( self.screen, (0,0,0), pygame.Rect(screen_unit[0] * 2, screen_unit[1] * 1, screen_unit[0] * 6, screen_unit[1] * 5), 4, 10 )

        #Write names of leader boards
        high_score_file = open("./score/score_board.txt", "r")
        content = high_score_file.readlines()
        for i in range(10):
            if i < len(content):
                line = content[i]
                re_line = line.replace("\n", "")
                values = re_line.split( ':' )
                if len(values) > 0:
                    self.screen.blit(font.render(values[0] + " - - - - -" + str(values[1]), True, PRETO), 
                                    ( screen_unit[0] * 2.2, screen_unit[1] * 1.2 + (screen_unit[1] // 2) * i))
        if len(content) > 10:
            self.screen.blit(font.render(" ... ", True, PRETO), ( screen_unit[0] * 2.2, screen_unit[1] * 5.8))
        
        #And options to get out
        text = font.render(str(self.__progress), True, PRETO)
        self.screen.blit(text, (self.screen.get_width() * .5, self.screen.get_height() * .65))
        
        text = font.render("Aperte ESPAÇO pra continuar", True, PRETO)
        self.screen.blit(text, (self.screen.get_width() * .5, self.screen.get_height() * .8))

        # Desenha a tela
        pygame.draw.rect(self.screen, PRETO, pygame.Rect(bar_position, bar_size), 2)
        pygame.draw.rect(self.screen, bar_color, pygame.Rect(bar_position[0] + 2, bar_position[1] + 2, full_bar, bar_size[1] - 2 * 2))

        pygame.display.flip()

        clock.tick()

        