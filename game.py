from module import Module
from scene import Scene
from state import State
from typing import Tuple, List
from utils import *

import pygame
import math

BACKGROUND_COLOR = (255, 255, 255)
RECTANGLE_COLOR = (135, 156, 232)
CENARIO_RECTANGLE_COLOR = (255, 0, 0)
FONT_COLOR = (255, 255, 255) 
WHITE = (255, 255, 255)

cursor_size = 48

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
    #Take last argument as texture map, so that will ignore the normal filling behaviour 
    # and follow the len of map for filling with correct texture (as int index of texture list)
    def __init__(self, surface:pygame.Surface, initial_pos:Tuple[int, int], 
                                               texture:pygame.Surface = None|List[pygame.Surface], texture_map:List[int] = None):
        #Setup
        self.surface = surface
        self.origin = initial_pos  
        self.pos = self.origin
        #Re-scale
        self.__s_width, self.__s_height = self.surface.get_width(), self.surface.get_height()
        sin = math.sin( math.radians( 45 ) ) 
        cos = math.cos( math.radians( 45 ) ) 
        size_x = abs( self.__s_width * sin ) + abs( self.__s_height * cos )
        size_y = abs( self.__s_width * cos ) + abs( self.__s_height * sin )
        self.surface = pygame.transform.scale( self.surface, (size_x * 2, size_y) )
        #Draw
        if texture != None:
            self.__texture = texture
            if texture_map != None:
                self.__texture_map = texture_map
            self.__draw()

    def __draw(self):

        t_width, t_height = self.__texture.get_width(), self.__texture.get_height()

        isometric_tiles = isometric_surface(self.__texture)

        s_center = self.surface.get_width() // 2

        for tile_horizontal_pos in range( self.__s_width  // t_width ):
            for tile_vertical_pos in range( self.__s_height // t_height ):
                
                current_pos = (tile_horizontal_pos * t_width, tile_vertical_pos * t_height)
                current_pos = isometric_point_displacement( current_pos )

                relocated_pos = (current_pos[0] + s_center - t_width, current_pos[1])
                self.surface.blit( isometric_tiles, relocated_pos )

    def hover(self, pos:Tuple[int,int], size:Tuple[int,int] ):

        #self.__draw()
        
        where_to = ( pos[0] - self.pos[0], pos[1] - self.pos[1] )
        where_to_iso = isometric_point_displacement(where_to)

        t_width, t_height = self.__texture.get_width(), self.__texture.get_height()
        for tile_horizontal_pos in range( size[0]  // t_width ):
            for tile_vertical_pos in range( size[1] // t_height ):
                
                current_pos = (tile_horizontal_pos * t_width, tile_vertical_pos * t_height)
                current_pos = isometric_point_displacement( current_pos )

                relocated_pos = (current_pos[0] + where_to_iso[0], current_pos[1] + where_to_iso[1])

                red_ver = pygame.Surface((t_width, t_height), pygame.SRCALPHA, 32)
                pygame.draw.rect(red_ver, (255,0,0), pygame.Rect(0, 0, t_width, t_height), 2)
                pygame.draw.rect(red_ver, (200,0,0), pygame.Rect(0, 0, t_width, t_height))

                self.surface.blit( red_ver, relocated_pos )

class Game(Module):

    def __init__(self, screen: pygame.Surface, state:State) -> None:
        super().__init__(screen, state)

        # ---- Sizes ----
        
        screen_rect = screen.get_rect()
        screen_size = (screen_rect.width, screen_rect.height)
        double_size = (screen_rect.width * 2, screen_rect.height * 2)
        half_size = DivideTuple(screen_size, 2)
        quarter_size = DivideTuple(screen_size, 4)

        # ---- Static gameobjects ----

        #Fonte: https://opengameart.org/content/tileable-grass-and-water
        #Exchange for isometric version
        water_surf = pygame.image.load( './sprites/water.png' )
        water_surf = water_surf.convert_alpha()
        #Exchange for pixel art landtile isometric sprite
        land_tile_surf = pygame.Surface((16, 16), pygame.SRCALPHA, 32)
        pygame.draw.rect(land_tile_surf, (0,154,23), pygame.Rect(0, 0, 16, 16))

        #Create a list of gameobjs named "static"
        self.__static_objs = [
            GameObject(pygame.Surface(double_size, pygame.SRCALPHA, 32), (-screen_size[0],-screen_size[1]), water_surf),
            GameObject(pygame.Surface(half_size, pygame.SRCALPHA, 32), quarter_size, land_tile_surf)
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
        pygame.draw.rect( self.screen, (155,103,60), self.screen.get_rect(), 10 )
        #Blit and move all "static objs by camera"
        for game_obj in self.__static_objs:
            game_obj.pos = ( game_obj.origin[0] - self.camera[0], game_obj.origin[1] - self.camera[1] )

            if colisao( game_obj.surface.get_rect(), pygame.Rect(current_pos[0], current_pos[1], cursor_size, cursor_size ) ):
                game_obj.hover( current_pos, (cursor_size,cursor_size) )

            self.screen.blit( game_obj.surface, game_obj.pos )
            pygame.draw.rect( self.screen, (255,0,0), game_obj.surface.get_rect(topleft = game_obj.pos), 1 )

        #UI
        self.__player_UI.draw( self.state.name, self.state.cenario, self.__currency, self.__satisfaction )
        self.screen.blit(self.__player_UI.surface, (0,0))

        pygame.display.flip()