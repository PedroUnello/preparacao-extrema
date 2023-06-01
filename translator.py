import pygame
from typing import Tuple, Dict, List
from objects import GameObject, tile_size

#Load all images of tiles
grass_img = pygame.image.load( './sprites/Subject 2.png' )
rugged_grass_img = pygame.image.load( './sprites/Subject 19.png' )
block_grass_img = pygame.image.load( './sprites/Subject 18.png' )
leaf_grass_img = pygame.image.load( './sprites/Subject 21.png' )
water_img = pygame.image.load( './sprites/Subject 3.png' )
small_building_img = pygame.image.load( './sprites/Subject 9.png')
wide_small_building_img = pygame.image.load( './sprites/Subject 10.png')
tall_building_img = pygame.image.load( './sprites/Subject 6.png')
house_building_img = pygame.image.load( './sprites/Subject 15.png')
inactive_volcano = pygame.image.load('./sprites/Subject 5.png')
#Enlists them in a dictionary
identified_objects = {
            '0': [(1, 1), grass_img, False, True, (0.1, 0.2)],
            '1': [(1, 1), rugged_grass_img, False, True, (0.1, 0.2)],
            '2': [(3, 2), small_building_img, True, True, (0.125, 0.215)],
            '3': [(3, 3), wide_small_building_img, True, True, (0.125, 0.215)],
            '4': [(2, 2), tall_building_img, True, True, (0.125, 0.215)],
            '5': [(3, 2), house_building_img, True, True, (0.125, 0.215)],
            '6': [(5, 5), inactive_volcano, True, True, (-0.325, 0.415)],
            '7': [(1, 1), block_grass_img, True, True, (0.1, 0.2)],
            '8': [(1, 1), leaf_grass_img, True, True, (0.1, 0.2)],
            ' ': None
}
#Generate map based on positions
def generate_map( map_path:str, map_size:Tuple[int, int], map_position:Tuple[int, int]) -> List[List[ any ]]:
    map_list = [ [None] * map_size[1] for _ in range( map_size[0] ) ]
    for i, line in enumerate(open( map_path, 'r').readlines()):
        line = line.replace("\n", "")
        for j, identifier in enumerate(line):
            equivalent_info = identified_objects[identifier]
            if equivalent_info != None:
                game_obj = GameObject(equivalent_info[0], equivalent_info[1], equivalent_info[2], equivalent_info[3], equivalent_info[4])
                game_obj.pos = (map_position[0] + tile_size[0] * (0.5 - game_obj.offset[0]) * (j - i), 
                                map_position[1] + tile_size[1] * (0.5 - game_obj.offset[1]) * (j + i))
                map_list[i][j] = game_obj
    return map_list