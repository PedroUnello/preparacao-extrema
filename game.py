from module import Module
from scene import Scene
from state import State
from typing import Tuple

import pygame

BACKGROUND_COLOR = (255, 255, 255)
RECTANGLE_COLOR = (135, 156, 232)
CENARIO_RECTANGLE_COLOR = (255, 0, 0)
FONT_COLOR = (255, 255, 255) 
WHITE = (255, 255, 255)

def clamp( value, min_val, max_val ):
    return max( min(value, max_val), min_val )

def isometric_surface( surface:pygame.Surface ) -> pygame.Surface:
    surface_rect = surface.get_rect()
    rot_surf = pygame.transform.rotate( surface, 45 )
    scale_surf = pygame.transform.scale( rot_surf, (surface_rect.width * 2, surface_rect.height ) )
    return scale_surf
 
def isometric_point_displacement(point:Tuple[int, int]) -> Tuple[int, int]:
    return (point[0] - point[1], ((point[0] + point[1])//2))

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
    def __init__(self, surface:pygame.Surface, initial_pos:Tuple[int, int], texture:pygame.Surface = None):
        
        self.surface = surface
        self.pos = initial_pos

        if texture != None:
            self.__texture = texture
            self.__draw()
        
    def __draw(self):

        surface_rect = self.surface.get_rect()
        tile_rect = self.__texture.get_rect()

        isometric_tiles = isometric_surface(self.__texture)

        for tile_horizontal_pos in range( surface_rect.width // 2 // tile_rect.width ):
            for tile_vertical_pos in range( surface_rect.height // 2 // tile_rect.height ):
                
                current_pos = (tile_horizontal_pos * tile_rect.width, tile_vertical_pos * tile_rect.height )

                self.surface.blit( isometric_tiles, isometric_point_displacement( current_pos ) )

class Game(Module):

    def __init__(self, screen: pygame.Surface, state:State) -> None:
        super().__init__(screen, state)

        # ---- Sizes ----
        
        screen_rect = screen.get_rect()
        double_size = (screen_rect.width * 2, screen_rect.height * 2)
        self.__screen_size =  (screen_rect.width, screen_rect.height)
        half_size = (screen_rect.width // 2, screen_rect.height // 2)
        quarter_size = (screen_rect.width // 4, screen_rect.height // 4)

        # ---- Static gameobjects ----

        #Fonte: https://opengameart.org/content/tileable-grass-and-water
        #Exchange for isometric version
        water_surf = pygame.image.load( './sprites/water.png' )
        #Exchange for pixel art landtile isometric sprite
        land_tile_surf = pygame.Surface((16, 16))
        pygame.draw.rect(land_tile_surf, (0,154,23), pygame.Rect(0, 0, 16, 16))

        #Create a list of gameobjs named "static"        
        self.__bg = GameObject(pygame.Surface(double_size), (-half_size[0],-half_size[1]), water_surf)
        self.__land = GameObject(pygame.Surface(half_size, pygame.SRCALPHA, 32), quarter_size, land_tile_surf)

        # ---- UI ----
        
        self.__player_UI = UI( self.screen.get_width(), 50 )
        
        # ---- Camera ----

        self.__last = pygame.mouse.get_pos()
        self.camera = quarter_size

        # ---- Game Values ----

        self.__currency = 10
        self.__satisfaction = 50

        

    def run(self, events):
        
        delta_value = (0, 0)

        for event in events:
            if event.type == pygame.MOUSEMOTION:
                current_pos = pygame.mouse.get_pos()
                delta_value = (current_pos[0] - self.__last[0], current_pos[1] - self.__last[1])
                delta_value = (clamp( delta_value[0], -1, 1 ), clamp( delta_value[1], -1, 1 ))
                self.__last = current_pos
            if event.type == pygame.KEYDOWN: #Remove below
                if event.key == pygame.K_LEFT:
                    self.state.scene = Scene.MENU
                if event.key == pygame.K_SPACE:
                    self.__currency += 15
        
        new_camera_x = clamp(self.camera[0] + delta_value[0], -self.__screen_size[0], self.__screen_size[0] )
        new_camera_y = clamp(self.camera[1] + delta_value[1], -self.__screen_size[1], self.__screen_size[1] )
        self.camera = (new_camera_x, new_camera_y)

        #Blit and move all "static objs by camera"
        self.__bg.pos = (self.__bg.pos[0] - delta_value[0], self.__bg.pos[1] - delta_value[1])
        self.__land.pos = (self.__land.pos[0] - delta_value[0], self.__land.pos[1] - delta_value[1])

        self.screen.blit(self.__bg.surface, self.__bg.pos)
        self.screen.blit(self.__land.surface, self.__land.pos)

        #UI
        self.__player_UI.draw( self.state.name, self.state.cenario, self.__currency, self.__satisfaction )
        self.screen.blit(self.__player_UI.surface, (0,0))
