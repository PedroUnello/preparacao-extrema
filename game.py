from module import Module
from scene import Scene
from state import State
from typing import Tuple, List
from utils import *

from enum import Enum
import pygame
import math

BACKGROUND_COLOR = (255, 255, 255)
RECTANGLE_COLOR = (135, 156, 232)
CENARIO_RECTANGLE_COLOR = (255, 0, 0)
FONT_COLOR = (255, 255, 255) 
WHITE = (255, 255, 255)

#Satisfacao formulada a base de
# Desastre ocorreu / danos maximos ->   -A pontos
#                                       + A * Y (medidas preventivas --+-- 2 caso nenhuma, -.5 por correta, .25 por errada )
#                                       + A * Z (verba --+-- -.2 por 10% de verba atual dentre maxima)
# Desastre ocorreu / danos minimos ->   -B pontos
#                                       + B * Y
#                                       + B * Z (verba --+-- 1 por < 10% de verba atual, -0.35 por 10% de verba atual enquanto < 50%, 0.05 por 10% )

cursor_size = 48

class Correct(Enum):
    NONE = 0
    STRETCH = 1
    DUPLICATE = 2
    SCALE = 3

class UI():
    def __init__(self, screen_width, UI_height = 50) -> None:
        self.__font = pygame.font.SysFont(None, 30)

        self.__width = screen_width
        self.__height = UI_height
        self.surface = pygame.surface.Surface(( self.__width, self.__height ), pygame.SRCALPHA, 32)

    def draw(self, name, cenario, currency, satisfaction ):
        name_text = self.__font.render(name, True, FONT_COLOR)
        cenario_text = self.__font.render(cenario, True, FONT_COLOR)

        # Definir a posição e o tamanho do retângulo
        rectangle_width = 200
        rectangle_height = 50
        rectangle_position = (self.__width - rectangle_width, 0)

        # Calcular a largura e a altura do retângulo necessário para conter o texto
        width_name_text, height_name_text = name_text.get_size()
        rectangle_width_2 = width_name_text + 20
        rectangle_height_2 = height_name_text + 20

        width_text_cenario, height_text_cenario = cenario_text.get_size()
        rectangle_width_cenario = width_text_cenario + 20
        rectangle_height_cenario = height_text_cenario + 20

        # Definir a posição do retângulo
        rectangle_position_2 = (10, 10)
        rectangle_position_cenario = ((self.__width - rectangle_width_cenario) // 2, 10)

        # Criar o retângulo
        rectangle = pygame.Rect(rectangle_position_2, (rectangle_width_2, rectangle_height_2))
        rectangle_cenario = pygame.Rect(rectangle_position_cenario, (rectangle_width_cenario, rectangle_height_cenario))

        # Preencher o retângulo com a cor desejada
        pygame.draw.rect(self.surface, RECTANGLE_COLOR, rectangle)
        pygame.draw.rect(self.surface, CENARIO_RECTANGLE_COLOR, rectangle_cenario)

        # Desenhar o texto do nome do jogador no retângulo
        self.surface.blit(name_text, (rectangle.x + 10, rectangle.y + 10))
        self.surface.blit(cenario_text, (rectangle_cenario.x + 10, rectangle_cenario.y + 10))

        # Definir a posição e o tamanho do ícone do dinheiro
        icon_width = 30
        icon_height = 30
        icon_position = (rectangle_position[0] + 5, rectangle_position[1] + 10)

        # Carregar o ícone do dinheiro e redimensioná-lo
        icon = pygame.image.load("./sprites/money.png")
        icon = pygame.transform.scale(icon, (icon_width, icon_height))

        # Desenhar o retângulo e o ícone na janela
        pygame.draw.rect(self.surface, WHITE, (rectangle_position, (rectangle_width, rectangle_height)))
        self.surface.blit(icon, icon_position)

        # Renderizar o texto do dinheiro
        money_text = self.__font.render("R$ " + str(currency), True, (0, 0, 0))

        # Definir a posição do texto dentro do retângulo
        money_position = (rectangle_position[0] + icon_width + 10, rectangle_position[1] + 10)

        # Desenhar o texto na janela
        self.surface.blit(money_text, money_position)

class GameObject():
    def __init__(self, surface:pygame.Surface, initial_pos:Tuple[int, int], 
                                               texture:pygame.Surface = None|List[List[pygame.Surface]], 
                                               stretch_inside:bool = False,
                                               correct_size:Correct = Correct.NONE):
        #Setup
        self.surface = surface
        self.origin = initial_pos  
        self.pos = self.origin
        
        self.__s_width, self.__s_height = self.surface.get_width(), self.surface.get_height()
        self.__stretch_inside = stretch_inside
        self.__correct_size = correct_size
        
        self.__texture, self.__t_size = self.__load( texture )
        
        

        #Draw
        self.draw()     

    def __load(self, texture) -> Tuple[ List[List[Tuple[pygame.Surface, Tuple[int, int]]]], Tuple[int, int] ]:
        
        self.surface.fill( (0, 0, 0, 0) )
        
        loaded_texture = []

        if type( texture ) == list:
            
            texture_height = 0
            texture_width = 0

            for i in range( len(texture) ):
                
                loaded_texture.append( [] )

                line = texture[i]
                line_size = len(line)
                
                if (line_size <= 0):
                    continue
                
                line_width = 0
                sorted_line = line
                sorted_line.sort(key=lambda e : e.get_height(), reverse=True)
                line_height = sorted_line[0].get_height()

                for j in range( len(line) ):

                    tile = line[j]
                    t_width, t_height = tile.get_width(), tile.get_height()
                    current_pos = (line_width, texture_height)

                    if (line_height > t_height and self.__stretch_inside):
                        tile = pygame.transform.scale( tile, ( t_width, line_height ) )
                
                    loaded_texture[i].append((tile, current_pos))
                    
                    line_width += t_width
                
                texture_height += line_height
                texture_width = max(line_width, texture_width)
        else:
            t_width, t_height = texture.get_width(), texture.get_height()
            for tile_horizontal_pos in range( self.__s_width  // t_width ):
                loaded_texture.append([])
                for tile_vertical_pos in range( self.__s_height // t_height ):
                    current_pos = (tile_horizontal_pos * t_width, tile_vertical_pos * t_height)
                    loaded_texture[tile_horizontal_pos].append((texture, current_pos))
            texture_width = tile_horizontal_pos * t_width
            texture_height = tile_vertical_pos * t_height

        return (loaded_texture, (texture_width, texture_height))

    def draw(self):
        self.surface.fill( (0, 0, 0, 0) )

        canvas = pygame.Surface( (self.__s_width, self.__s_height), pygame.SRCALPHA, 32)
        for line in self.__texture:
            for tile in line:
                canvas.blit(tile[0], tile[1])

        texture_width, texture_height = self.__t_size
        smaller_width =  texture_width < self.__s_width 
        smaller_height = texture_height < self.__s_height 
        if smaller_width or smaller_height:
            match self.__correct_size:
                case Correct.SCALE:
                    new_width = self.__s_width * ((self.__s_width - texture_width) if smaller_width else 1)
                    new_height = self.__s_height * ((self.__s_height - texture_height) if smaller_height else 1)
                    canvas = pygame.transform.scale( canvas, (new_width, new_height))
                case Correct.STRETCH:
                    if (smaller_height and len(self.__texture[-1])) > 0:
                        line = self.__texture[-1]
                        sorted_line = line
                        sorted_line.sort(key=lambda e : e.get_height(), reverse=True)
                        line_height = sorted_line[0].get_height()
                        line_width = 0
                        pos_y = texture_height - line_height
                        for tile in line:
                            t_width = tile.get_width()
                            tile = pygame.transform.scale( tile, (t_width, self.__s_height + (self.__s_height - texture_height) * 2) )
                            canvas.blit( tile, (line_width, pos_y) )
                            line_width += t_width
                    if (smaller_width):
                        for i in range( len(self.__texture) ):
                            if (len(self.__texture[i])) > 0:
                                sorted_line = self.__texture[i]
                                sorted_line.sort(key=lambda e : e.get_height(), reverse=True)
                                line_height = sorted_line[0].get_height()
                                tile = self.__texture[i][-1]
                                pos_x = texture_width - tile.get_width()
                                tile = pygame.transform.scale( tile, (self.__s_width + (self.__s_width - texture_width) * 2, tile.get_height()) )
                                canvas.blit(tile, (pos_x, line_height))
                    if (smaller_height and smaller_width):
                        pass
                case Correct.DUPLICATE:
                    while (smaller_height or smaller_width):        
                        if (smaller_height and smaller_width):
                            canvas.blit(canvas, (texture_width, texture_height))
                        if (smaller_height):
                            canvas.blit(canvas, (0, texture_height))
                            texture_height += texture_height
                        if (smaller_width):
                            canvas.blit(canvas, (texture_width, 0))
                            texture_width += texture_width
                        smaller_width = texture_width < self.__s_width 
                        smaller_height = texture_height < self.__s_height 

        self.surface.blit(canvas, (0,0))

    def hover(self, pos:Tuple[int, int]):

        relocated_pos = (pos[0] - self.pos[0], pos[1] - self.pos[1])
        relocated_rect = pygame.Rect(relocated_pos[0], relocated_pos[1], 1, 1)
        for line in self.__texture:
            for tile in line:
                if colisao(relocated_rect, tile[0].get_rect( topleft = tile[1] )):
                    t_width, t_height = tile[0].get_width(), tile[0].get_height()
                    red_ver = pygame.Surface((t_width, t_height), pygame.SRCALPHA, 32)
                    pygame.draw.rect(red_ver, (100,0,0, 100), pygame.Rect(0, 0, t_width, t_height))
                    pygame.draw.rect(red_ver, (255,0,0), pygame.Rect(0, 0, t_width, t_height), 2)
                    self.surface.blit( red_ver, tile[1] )

class Game(Module):
    def __init__(self, screen: pygame.Surface, state:State) -> None:
        super().__init__(screen, state)

        # ---- Sizes ----
        
        screen_rect = screen.get_rect()
        screen_size = (screen_rect.width, screen_rect.height)
        double_size = (screen_rect.width * 2, screen_rect.height * 2)
        half_size = DivideTuple(screen_size, 2)
        quarter_size = DivideTuple(screen_size, 4)

        # ---- GameObjects ----

        self.__gameobject_canvas = pygame.Surface( (screen.get_width(), screen.get_height()), pygame.SRCALPHA, 32 ) 


        #Fonte: https://opengameart.org/content/tileable-grass-and-water
        #Exchange for isometric version
        water_surf = pygame.image.load( './sprites/water.png' )
        water_surf = water_surf.convert_alpha()
        #Exchange for pixel art landtile isometric sprite
        grass_tile_surf = pygame.Surface((16, 16), pygame.SRCALPHA, 32)
        pygame.draw.rect(grass_tile_surf, (0,154,23), pygame.Rect(0, 0, 16, 16))
        dirt_tile_surf = pygame.Surface((16, 16), pygame.SRCALPHA, 32)
        pygame.draw.rect(dirt_tile_surf, (155,118,83), pygame.Rect(0, 0, 16, 16))

        map_sprites = [ 
            [ {
                    '#': grass_tile_surf,
                    '.': dirt_tile_surf,
                    '-': water_surf
                }[tile] for tile in line.replace("\n", "")
            ] for line in open( '/home/pedrounello/Área de Trabalho/preparacao-extrema/cenarios/Toquio.txt', 'r').readlines() if len(line.replace("\n", "")) > 0
        ]

        #Create a list of gameobjs named "static"
        self.__static_objs = [
            GameObject(pygame.Surface(double_size, pygame.SRCALPHA, 32), (-screen_size[0],-screen_size[1]), water_surf),
            GameObject(pygame.Surface(half_size, pygame.SRCALPHA, 32), quarter_size, grass_tile_surf)
        ]

        # ---- UI ----
        
        self.__player_UI = UI( self.screen.get_width(), 50 )
        
        # ---- Camera ----

        self.__last = pygame.mouse.get_pos()
        self.camera = (0, 0)

        # ---- Game Values ----

        self.__currency = 10
        self.__satisfaction = 50

    def run(self, events):
        
        delta_value = (0, 0)
        current_pos = pygame.mouse.get_pos()

        for event in events:
            if event.type == pygame.MOUSEMOTION:        
                delta_value = (current_pos[0] - self.__last[0], current_pos[1] - self.__last[1])
                delta_value = (clamp( delta_value[0], -1, 1 ), clamp( delta_value[1], -1, 1 ))
                self.__last = current_pos
            if event.type == pygame.KEYDOWN: #Remove below
                if event.key == pygame.K_LEFT:
                    self.state.scene = Scene.MENU
                if event.key == pygame.K_SPACE:
                    self.__currency += 15
                if event.key == pygame.K_RIGHT:
                    self.state.scene = Scene.SCORE
        
        screen_x = self.screen.get_width()
        screen_y = self.screen.get_height()
        new_camera_x = clamp(self.camera[0] + delta_value[0] * 10, -screen_x, screen_x )
        new_camera_y = clamp(self.camera[1] + delta_value[1] * 10, -screen_y, screen_y )
        self.camera = (new_camera_x, new_camera_y)

        self.screen.fill((0,0,40))
        self.__gameobject_canvas.fill((0,0,0,0))

        pygame.draw.rect( self.screen, (155,103,60), self.screen.get_rect(), 10 )
        
        #Blit and move all "static objs by camera"
        for game_obj in self.__static_objs:
            game_obj.pos = ( game_obj.origin[0] - self.camera[0], game_obj.origin[1] - self.camera[1] )

            
            #if colisao( game_obj.surface.get_rect(), pygame.Rect(current_pos[0], current_pos[1], cursor_size, cursor_size ) ):
                #game_obj.draw()
                #game_obj.hover( current_pos )

            self.__gameobject_canvas.blit( game_obj.surface, game_obj.pos )
            pygame.draw.rect( self.__gameobject_canvas, (255,0,0), game_obj.surface.get_rect(topleft = game_obj.pos), 1 )

        isometric_canvas = isometric_surface(self.__gameobject_canvas)
        self.screen.blit(isometric_canvas, ( 0, 0 ))

        #UI
        self.__player_UI.draw( self.state.name, self.state.cenario, self.__currency, self.__satisfaction )
        self.screen.blit(self.__player_UI.surface, (0,0))

        pygame.display.flip()