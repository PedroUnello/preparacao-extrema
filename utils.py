from typing import Tuple
import pygame

def clamp( value, min_val, max_val ):
    return max( min(value, max_val), min_val )

def isometric_surface( surface:pygame.Surface ) -> pygame.Surface:
    rot_surf = pygame.transform.rotate( surface, 45 )
    rot_rect = rot_surf.get_rect(center = surface.get_rect().bottomright)    
    scale_surf = pygame.transform.scale( rot_surf, (rot_rect.width * 2, rot_rect.height) )
    return scale_surf
 
def isometric_point_displacement(point:Tuple[int, int]) -> Tuple[int, int]:
    return (point[0] - point[1], ((point[0] + point[1]) // 2))

def DivideTuple( a:Tuple, b:int ) -> Tuple:
    return tuple( elm / b for elm in a )

#Fonte: Leandro Pupo
def lerp(value1, value2, factor):
    return value1+(value2-value1)*factor

#Fonte: Leandro Pupo
def colisao(rect1:pygame.Rect, rect2:pygame.Rect) -> bool:
    x_1, y_1 = rect1.topleft[0], rect1.topleft[1]
    x_2, y_2 = rect2.topleft[0], rect2.topleft[1]
    return x_1 < x_2 + rect2.width and x_1 + rect1.width > x_2 and y_1 < y_2 + rect2.height and rect1.height + y_1 > y_2

#Fonte: Leandro Pupo
def colisao_isometrica(rect1:pygame.Rect, rect2:pygame.Rect) -> bool:
    x_1, y_1 = isometric_point_displacement(rect1.topleft)
    x_2, y_2 = isometric_point_displacement(rect2.topleft)
    return x_1 < x_2 + rect2.width and x_1 + rect1.width > x_2 and y_1 < y_2 + rect2.height and rect1.height + y_1 > y_2
 