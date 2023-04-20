from module import Module
from scene import Scene
from typing import Tuple

import pygame

def clamp( value, min_val, max_val ):
    return max( min(value, max_val), min_val )

def isometric_surface( surface:pygame.surface ) -> pygame.Surface:
    surface_rect = surface.get_rect()
    rot_surf = pygame.transform.rotate( surface, 45 )
    scale_surf = pygame.transform.scale( rot_surf, (surface_rect.width, surface_rect.height // 2) )
    return scale_surf

def isometric_point_displacement(point:Tuple[int, int]) -> Tuple[int, int]:
    return (point[0] - point[1], ((point[0] + point[1])//2))

class GameObject():
    def __init__(self, surface:pygame.Surface, initial_pos:Tuple[int, int], texture:pygame.Surface = None):
        
        self.surface = surface
        self.pos = initial_pos

        if texture != None:
            self.__texture = texture
            self.__draw()

        """
        cos = numpy.cos(0)
        sin = numpy.sin(0)

        
        surf_array = pygame.surfarray.array3d( self.surface )
        surf_height = len(surf_array)
        surf_width = len(surf_array[0])
        for i in range(surf_width):
            x = surf_width // 2 - i
            for j in range(surf_height):
                y = j + 250
                z = j - surf_height // 2
                 # rotation
                px = (x * cos - y * sin)
                py = (x * sin + y * cos)

                # floor projection and transformation
                floor_x = px / z 
                floor_y = py / z 

                # floor pos and color
                floor_pos = int(floor_x), int(floor_y )
                floor_col = surf_array[floor_pos]




                floor_col = (floor_col[0] ,
                             floor_col[1] ,
                             floor_col[2])


                # fill screen array
                surf_array[i, j] = floor_col

        self.surface = pygame.surfarray.make_surface( surf_array )
        """
    def __draw(self):

        surface_rect = self.surface.get_rect()
        tile_rect = self.__texture.get_rect()

        for tile_horizontal_pos in range( surface_rect.width // tile_rect.width ):
            for tile_vertical_pos in range( surface_rect.height // tile_rect.height ):
                
                current_pos = (tile_horizontal_pos * tile_rect.width, tile_vertical_pos * tile_rect.height )

                self.surface.blit( self.__texture, current_pos )

class Game(Module):

    def __init__(self, screen: pygame.Surface, state: Scene) -> None:
        super().__init__(screen, state)

        screen_rect = screen.get_rect()
        double_size = (screen_rect.width * 2, screen_rect.height * 2)
        self.__screen_size =  (screen_rect.width, screen_rect.height)
        half_size = (screen_rect.width // 2, screen_rect.height // 2)
        quarter_size = (screen_rect.width // 4, screen_rect.height // 4)

        #Fonte: https://opengameart.org/content/tileable-grass-and-water
        #Exchange for isometric version
        water_surf = pygame.image.load( './sprites/water.png' )
        #Exchange for pixel art landtile isometric sprite
        land_tile_surf = pygame.Surface((16, 16))
        pygame.draw.rect(land_tile_surf, (0,154,23), pygame.Rect(0, 0, 16, 16))

        #Create a list of gameobjs named "static"        
        self.__bg = GameObject(pygame.Surface(double_size), (-half_size[0],-half_size[1]), water_surf)
        self.__land = GameObject(pygame.Surface(half_size), quarter_size, land_tile_surf)

        self.__last = pygame.mouse.get_pos()
        self.camera = quarter_size


    def run(self, events):
        
        delta_value = (0, 0)

        for event in events:
            if event.type == pygame.MOUSEMOTION:
                current_pos = pygame.mouse.get_pos()
                delta_value = (current_pos[0] - self.__last[0], current_pos[1] - self.__last[1])
                delta_value = (clamp( delta_value[0], -1, 1 ), clamp( delta_value[1], -1, 1 ))
                self.__last = current_pos
        
        new_camera_x = clamp(self.camera[0] + delta_value[0], -self.__screen_size[0], self.__screen_size[0] )
        new_camera_y = clamp(self.camera[1] + delta_value[1], -self.__screen_size[1], self.__screen_size[1] )
        self.camera = (new_camera_x, new_camera_y)

        #Blit and move all "static objs by camera"
        self.__bg.pos = (self.__bg.pos[0] - delta_value[0], self.__bg.pos[1] - delta_value[1])
        self.__land.pos = (self.__land.pos[0] - delta_value[0], self.__land.pos[1] - delta_value[1])

        self.screen.blit(self.__bg.surface, self.__bg.pos)
        self.screen.blit(self.__land.surface, self.__land.pos)