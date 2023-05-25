from module import Module
from scene import Scene
from state import State
from typing import Tuple, List
from utils import *
from datetime import timedelta

from enum import Enum
import pygame
import math

BACKGROUND_COLOR = (255, 255, 255)
RECTANGLE_COLOR = (135, 156, 232, 50)
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

        # Load images and persist in a attribute (image_list)
        icon_width, icon_height = 30, 30
        money = pygame.image.load("./sprites/money.png")
        money = pygame.transform.scale(money, (icon_width, icon_height))
        integrity = pygame.image.load("./sprites/Integrity.png")
        integrity = pygame.transform.scale(integrity, (icon_width, icon_height))
        satisfaction_bar = pygame.image.load("./sprites/Satisfaction_bar.png")
        satisfaction_bar = pygame.transform.scale(satisfaction_bar, (self.__width * 0.3, self.__height * 0.35))
        overwatch = pygame.image.load("./sprites/overwatch.png")
        overwatch = pygame.transform.scale(overwatch, (self.__width * 0.15 * 0.5, self.__height * 0.35))
        self.__image_list = [
            money,
            integrity,
            satisfaction_bar,
            overwatch
        ]

    def draw(self, name, cenario, currency, satisfaction, city_integrity, time_left, additional_info_object = None ):

        self.surface.fill((0,0,0,0))

        #Section - Player info
        player_info_rect = pygame.rect.Rect( 0, 0, self.__width * 0.4, self.__height )
        player_info = pygame.surface.Surface( player_info_rect.size, pygame.SRCALPHA, 32 )
        pygame.draw.rect(player_info, RECTANGLE_COLOR, player_info.get_rect(), 0, 20)
        pygame.draw.rect(player_info, (155, 186, 252), player_info.get_rect(), 10, 20)
        #Section - Game Info
        game_info_rect = pygame.rect.Rect( self.__width * 0.425, self.__height * 0.2, self.__width * 0.15, self.__height * 0.5 )
        game_info = pygame.surface.Surface( game_info_rect.size, pygame.SRCALPHA, 32 )
        pygame.draw.rect(game_info, RECTANGLE_COLOR, game_info.get_rect(), 0, 50)
        pygame.draw.rect(game_info, (155, 186, 252), game_info.get_rect(), 5, 50)
        #Section - Overwatch info
        overwatch_info_rect = pygame.rect.Rect( self.__width * 0.835, self.__height * 0.1, self.__width * 0.15, self.__height )
        overwatch_info = pygame.surface.Surface( overwatch_info_rect.size, pygame.SRCALPHA, 32 )
        deslocated_rect = overwatch_info.get_rect()
        #Draw borders
        pygame.draw.polygon(overwatch_info, (155, 186, 252), 
                            [
                                (deslocated_rect.width * 0.8, deslocated_rect.height * 0.05), 
                                (deslocated_rect.width * 0.6, deslocated_rect.height * 0.35),
                                (deslocated_rect.width * 0.8, deslocated_rect.height * 0.65),
                                (deslocated_rect.width, deslocated_rect.height * 0.35)
                            ])
        pygame.draw.polygon(overwatch_info, RECTANGLE_COLOR, 
                            [
                                (deslocated_rect.width * 0.8, deslocated_rect.height * 0.05), 
                                (deslocated_rect.width * 0.6, deslocated_rect.height * 0.35),
                                (deslocated_rect.width * 0.8, deslocated_rect.height * 0.65),
                                (deslocated_rect.width, deslocated_rect.height * 0.35)
                            ], 5)
        pygame.draw.circle(overwatch_info, RECTANGLE_COLOR, (deslocated_rect.width * 0.8, deslocated_rect.height * 0.35), deslocated_rect.width * 0.125)
        #Mask photo in a circle picture (using a subsurface with masking circle and blend)
        photo_position = (deslocated_rect.width * 0.8 - self.__image_list[3].get_width() * 0.5, deslocated_rect.height * 0.35  - self.__image_list[3].get_height() * 0.5)
        photo_mask = pygame.surface.Surface( self.__image_list[3].get_size(), pygame.SRCALPHA )
        pygame.draw.circle(photo_mask, (255,255,255,255), (self.__image_list[3].get_width() * 0.5, self.__image_list[3].get_height() * 0.5), deslocated_rect.width * 0.125)
        photo_mask.blit(self.__image_list[3], (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        #Blit result.
        overwatch_info.blit(photo_mask, photo_position)
        #Section - Overwatch Chat
        overwatch_chat_rect = pygame.rect.Rect( self.__width * 0.6, self.__height * 0.1, self.__width * 0.32, self.__height )
        overwatch_chat = pygame.surface.Surface( overwatch_chat_rect.size, pygame.SRCALPHA, 32 )
        deslocated_rect = overwatch_chat.get_rect()
        chat_rect = pygame.Rect( deslocated_rect.width * 0.05, deslocated_rect.height * 0.05, deslocated_rect.width * 0.95, deslocated_rect.height * 0.8 )
        pygame.draw.rect(overwatch_chat, RECTANGLE_COLOR, chat_rect, 0, 5)
        pygame.draw.rect(overwatch_chat, (155, 186, 252), chat_rect, 5, 5)

        name_text = self.__font.render(name, True, FONT_COLOR)
        cenario_text = self.__font.render(cenario, True, FONT_COLOR)
        money_text = self.__font.render("R$ " + str(currency), True, FONT_COLOR)
        satisfaction_text = self.__font.render(str(satisfaction) + "%", True, FONT_COLOR)
        city_integrity_text = self.__font.render(str(city_integrity) + "%", True, FONT_COLOR)
        time_left_text = self.__font.render(str(timedelta(seconds=time_left)), True, FONT_COLOR)

        bar_position_x = player_info_rect.width * 0.5 - self.__image_list[2].get_width() * 0.5
        bar_position_y = player_info_rect.height * 0.3

        #Draw all texts
        player_info.blit(name_text, (player_info_rect.width * 0.5 - name_text.get_width() * 0.5, player_info_rect.height * 0.1))
        player_info.blit(self.__image_list[0], (player_info_rect.width * 0.53 + city_integrity_text.get_width() * 0.2, player_info_rect.height * 0.65))
        player_info.blit(money_text, (player_info_rect.width * 0.6 + city_integrity_text.get_width() * 0.2, player_info_rect.height * 0.7))
        player_info.blit(self.__image_list[2], (bar_position_x, bar_position_y))
        player_info.blit(satisfaction_text, (player_info_rect.width * 0.08 - satisfaction_text.get_width() * 0.5, player_info_rect.height * 0.3))
        player_info.blit(self.__image_list[1], (player_info_rect.width * 0.23, player_info_rect.height * 0.65))
        player_info.blit(city_integrity_text, (player_info_rect.width * 0.3, player_info_rect.height * 0.7))
        game_info.blit(cenario_text, (game_info_rect.width * 0.5 - cenario_text.get_width() * 0.5, game_info_rect.height * 0.5))
        game_info.blit(time_left_text, (game_info_rect.width * 0.5 - time_left_text.get_width() * 0.5, game_info_rect.height * 0.2))
        
        indicator_pos = lerp(bar_position_x, bar_position_x + self.__image_list[2].get_width() , satisfaction / 100 )
        pygame.draw.polygon(player_info, WHITE, 
                            [
                                (indicator_pos - 10, bar_position_y - 5), 
                                (indicator_pos + 10, bar_position_y - 5), 
                                (indicator_pos, bar_position_y + 5)
        ])

        self.surface.blit(player_info, player_info_rect.topleft)
        self.surface.blit(game_info, game_info_rect.topleft)
        if additional_info_object != None:
            self.surface.blit(overwatch_chat, overwatch_chat_rect.topleft)
        self.surface.blit(overwatch_info, overwatch_info_rect.topleft)

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
            ] for line in open( './cenarios/Toquio.txt', 'r').readlines() if len(line.replace("\n", "")) > 0
        ]

        #Create a list of gameobjs named "static"
        self.__static_objs = [
            GameObject(pygame.Surface(double_size, pygame.SRCALPHA, 32), (-screen_size[0],-screen_size[1]), water_surf),
            GameObject(pygame.Surface(half_size, pygame.SRCALPHA, 32), quarter_size, grass_tile_surf)
        ]

        # ---- UI ----
        
        self.__player_UI = UI( self.screen.get_width(), self.screen.get_height() * 0.185 )
        self.__show = True
        
        # ---- Camera ----

        self.__last = pygame.mouse.get_pos()
        self.camera = (0, 0)

        # ---- Game Values ----

        self.__currency = 10
        self.__satisfaction = 50
        self.__city_integrity = 100
        self.__time_left = 600

    def run(self, events, clock):

        game_finished = self.__satisfaction <= 0 or self.__time_left <= 0 or self.__city_integrity <= 0

        if game_finished:
            #Fill in score
            self.state.scene = Scene.SCORE

        self.__satisfaction = clamp(self.__satisfaction, 0, 100)
        self.__city_integrity = clamp(self.__city_integrity, 0, 100)

        delta_value = (0, 0)
        current_pos = pygame.mouse.get_pos()

        for event in events:
            if event.type == pygame.MOUSEMOTION:        
                delta_value = (current_pos[0] - self.__last[0], current_pos[1] - self.__last[1])
                delta_value = (clamp( delta_value[0], -1, 1 ), clamp( delta_value[1], -1, 1 ))
                self.__last = current_pos
            if event.type == pygame.KEYDOWN: 
                if event.key == pygame.K_q:
                    self.__show = not self.__show 
                #Remove below
                if event.key == pygame.K_LEFT:
                    self.state.scene = Scene.MENU
                if event.key == pygame.K_SPACE:
                    self.__satisfaction += 15
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
        if self.__show:
            self.__player_UI.draw( self.state.name, self.state.cenario, self.__currency, self.__satisfaction, self.__city_integrity, int(self.__time_left) )
            self.screen.blit(self.__player_UI.surface, (0,0))

        pygame.display.flip()

        self.__time_left -= clock.tick() / 1000