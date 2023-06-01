import pygame
from typing import Tuple, Dict
from utils import *
import random

tile_size = (25,25)

class GameObject():
    def __init__(self,  tiles:Tuple[int, int],  
                        texture:pygame.Surface,
                        obstacle:bool = False,
                        isometric:bool = False,
                        offset:Tuple[float,float] = (0,0)):
        
        #Setup
        size = (tiles[0] * tile_size[0], tiles[1] * tile_size[1])

        self.tiles = tiles

        self.surface = pygame.surface.Surface( size, pygame.SRCALPHA, 32 )
        self.surface.fill( (0, 0, 0, 0) )
        
        self.pos = (0, 0)

        self.__texture = pygame.transform.scale( texture, size )
        self.__isometric = isometric
        self.__obstacle = obstacle

        self.offset = offset

        #Draw
        self.draw()     
    
    def draw(self):

        self.surface.fill( (0, 0, 0, 0) )
        self.surface.blit(self.__texture, (0,0))
        
        if not self.__isometric:
            self.surface = isometric_surface( self.surface )

    def hover(self):

        if self.__obstacle:
            red_ver = pygame.Surface(self.__texture.get_size(), pygame.SRCALPHA, 32)
            pygame.draw.rect(red_ver, (100,0,0, 100), self.__texture.get_rect())
            pygame.draw.rect(red_ver, (255,0,0), self.__texture.get_rect(), 2)
            red_ver = isometric_surface(red_ver)
            red_ver = pygame.transform.scale( red_ver, self.surface.get_size() )
            self.surface.blit( red_ver, (0,0) )
        else:
            green_ver = pygame.Surface(self.__texture.get_size(), pygame.SRCALPHA, 32)
            pygame.draw.rect(green_ver, (0,100,0, 100), self.__texture.get_rect())
            pygame.draw.rect(green_ver, (0,255,0), self.__texture.get_rect(), 2)
            green_ver = isometric_surface(green_ver)
            green_ver = pygame.transform.scale( green_ver, self.surface.get_size() )
            self.surface.blit( green_ver, (0,0) )

        return self.__obstacle

class Disaster(GameObject):
    def __init__(self, damage:float, area:Tuple[int,int], safety_measures:Dict[GameObject, float], duration:float,
                        tiles:Tuple[int, int],  
                        texture:pygame.Surface,
                        isometric:bool = False,
                        offset:Tuple[float,float] = (0,0)):
        super().__init__(tiles, texture, isometric, offset)

        self.damage = damage
        self.area= area
        self.safety_measures = safety_measures
        self.duration = duration

class Measure(GameObject):
    def __init__(self, response_time:float, area:Tuple[int,int], name:str, description:str, price:float,
                        tiles:Tuple[int, int],  
                        texture:pygame.Surface,
                        isometric:bool = False,
                        offset:Tuple[float,float] = (0,0)):
        super().__init__(tiles, texture, True, isometric, offset)
        
        self.area = area
        self.name = name
        self.description = description
        self.price = price

class Person(GameObject):
    def __init__(self,  tiles:Tuple[int, int] = (1, 1),  
                        texture:pygame.Surface = pygame.surface.Surface( (0,0) ),
                        isometric:bool = False,
                        offset:Tuple[float,float] = (0,0)):
        super().__init__(tiles, texture, isometric, offset)
    
        up_left = pygame.image.load('sprites\Pessoa (8).png')
        up_left = up_left.convert_alpha()
        up_left = pygame.transform.scale( up_left, (tile_size[0] // 2, tile_size[1] // 2) )
        up = pygame.image.load('sprites\Pessoa (7).png')
        up = up.convert_alpha()
        up = pygame.transform.scale( up, (tile_size[0] // 2, tile_size[1] // 2) )
        up_right = pygame.image.load('sprites\Pessoa (6).png')
        up_right.convert_alpha()
        up_right = pygame.transform.scale( up_right, (tile_size[0] // 2, tile_size[1] // 2) )
        down_left = pygame.image.load('sprites\Pessoa (2).png')
        down_left = down_left.convert_alpha()
        down_left = pygame.transform.scale( down_left, (tile_size[0] // 2, tile_size[1] // 2) )
        down = pygame.image.load('sprites\Pessoa (3).png')
        down = down.convert_alpha()
        down = pygame.transform.scale( down, (tile_size[0] // 2, tile_size[1] // 2) )
        down_right = pygame.image.load('sprites\Pessoa (4).png')
        down_right = down_right.convert_alpha()
        down_right = pygame.transform.scale( down_right, (tile_size[0] // 2, tile_size[1] // 2) )

        self.__directions = [
            [up_left, up, up_right],
            [down_left, down, down_right]
        ]

    def move(self, map_size):
        
        x = random.choice( [-1, 0, 1] )
        y = random.choice( [-1, 0, 1] )

        if self.pos[0] < 0:
            x = 1
        if self.pos[0] > map_size[0] * tile_size[0]:
            x = -1
        if self.pos[1] < 0: 
            y = 1
        if self.pos[1] > map_size[1] * tile_size[1]:
            y = -1

        movement = self.__directions[0 if y == -1 else 1][x + 1]
        self.surface.fill((0,0,0,0))
        self.surface.blit(movement, (0,0))
        
        self.pos = ( self.pos[0] + x, self.pos[1] + y )