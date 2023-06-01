from module import Module
from scene import Scene
from state import State
from translator import generate_map, water_img
from typing import List
from utils import *
from objects import *
from datetime import timedelta

from enum import Enum
import pygame
import copy

BACKGROUND_COLOR = (255, 255, 255)
RECTANGLE_COLOR = (135, 156, 232, 50)
CENARIO_RECTANGLE_COLOR = (255, 0, 0)
FONT_COLOR = (255, 255, 255) 
WHITE = (255, 255, 255)

cursor_size = [1, 1]
current_measures = [None]
map_size = (50, 50)
ocean_size = (1, 1)

def satisfaction_calculator( safety_objects:List[any], budget_left:float, budget_max:float ) -> float:
    
    
    #Satisfacao formulada a base de
    # Desastre ocorreu / danos maximos ->   -A pontos
    #                                       + A * Y (medidas preventivas --+-- 2 caso nenhuma, -.5 por correta, .25 por errada )
    #                                       + A * Z (verba --+-- -.2 por 10% de verba atual dentre maxima)
    # Desastre ocorreu / danos minimos ->   -B pontos
    #                                       + B * Y
    #                                       + B * Z (verba --+-- 1 por < 10% de verba atual, -0.35 por 10% de verba atual enquanto < 50%, 0.05 por 10% )

    satisfaction_increment = 0

    correct_measures = len([ measure for measure in safety_objects if type(measure) == GameObject ])
    budget_percentage = int((budget_left / budget_max) * 10 )

    serious_damage = False

    if serious_damage:
        positive_increment_measures = -0.5 * correct_measures
        negative_increment_measures = 0.25 * (len(safety_objects) - correct_measures)
        satisfaction_increment -= 5 + 5 * ( 2 + negative_increment_measures + positive_increment_measures ) + 5 * ( -0.2 * budget_percentage)
    else:
        positive_increment_measures = -1 * correct_measures
        negative_increment_measures = 0.125 * (len(safety_objects) - correct_measures)
        positive_increment_budget = -0.35 * budget_percentage if budget_percentage < 5 else 0
        negative_increment_budget = 0.05 * budget_percentage if budget_percentage >= 5 else 0
        fixed_increment_budget = 1 + positive_increment_budget + negative_increment_budget
        satisfaction_increment -= 2 + 2 * ( 1 + negative_increment_measures + positive_increment_measures ) + 2 * fixed_increment_budget

    return satisfaction_increment

def disaster_master_AI( time_left:int, time_max:int, satisfaction:float, integrity:float, disaster_quantity:int ):
    time_factor = 1 - time_left / time_max
    satisfaction_factor = satisfaction / 100
    integrity_factor = integrity / 100
    chance = (disaster_quantity / 10) + time_factor * 0.2 + satisfaction_factor * 0.1 + integrity_factor * 0.3 if disaster_quantity < 5 else 0 
    return random.random() <= chance

alarme_tectonico = Measure(10, (15, 15), 'Alarme Tectônico', 
                           """Um alarme que notifica os residentes sobre atividades tectonicas fora do comúm,\n 
o que precede terremotos, tsunamis e mais, a eficácia é atrelada ao funcionamento\n
das instituições que medem atividades tectonicas, assim como a distância dos residentes""",
                           560, (1, 1),  pygame.image.load('./sprites/Subject 12.png'), True, (0.825, 0.815) )
barragem_oceanica = Measure(5, (3, 3), 'Barragem Oceânica', 
                            """Uma parede sólida, alta e muito reforçada, serve para barrar o avanço d'água\n
mesmo quando em alturas fora do comúm (em um Tsunami, por exemplo), ainda sim,\n
faz-se perigoso e impossível subir estas estruturas alto o suficiente para proteger\n
contra Tsunamis, por risco de deslizamentos e desastres não-naturais""",
                            245.5, (3, 1),  pygame.image.load('./sprites/Subject 4.png'), True, (0, 0) )
abrigo_tornado = Measure(25, (10, 10), 'Abrigo de tornado', 
                            """Um abrigo subterrâneo, feito especialmente para abrigar pessoas fora do alcance\n
de forças extremas na superfície, muito útil frente a tornados, porém não tão útil com atividades\n
tectonicas, pois não há proteção contra enchente ou muito valor contra terremotos""",
                            1300.5, (1, 1),  pygame.image.load('./sprites/Subject 5.png'), True, (0, 0) )

list_of_measures = [
    alarme_tectonico,
    barragem_oceanica,
    abrigo_tornado
]

tornado = Disaster(0.005, (4, 4), {abrigo_tornado:10}, 10, (2, 2), pygame.image.load('./sprites/Subject 5.png'), True, (0, 0) )
tsunami = Disaster(0.005, (4, 4), {alarme_tectonico:5, barragem_oceanica:10}, 20, (2, 2), pygame.image.load('./sprites/Subject 5.png'), True, (0, 0) )
volcano = Disaster(0.005, (10, 10), {alarme_tectonico:5}, 5, (5, 5), pygame.image.load('./sprites/Subject 5.png'), True, (0, 0) )

list_of_disaster = [
    tornado,
    tsunami,
    volcano
]

class UI():
    def __init__(self, screen:pygame.Surface, UI_height = 50) -> None:
        
        self.__font = pygame.font.SysFont(None, 30)

        self.__width = screen.get_rect().width
        self.__height = UI_height
        self.surface = pygame.surface.Surface(( self.__width, screen.get_rect().height ), pygame.SRCALPHA, 32)

        # Load images and persist in a attribute (image_list)
        icon_width, icon_height = 30, 30
        money = pygame.image.load("./sprites/Subject - cópia 3.png")
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

        self.__usable_bar = pygame.surface.Surface( (self.__width, UI_height * 0.5), pygame.SRCALPHA, 32 )

    def draw(self, name, cenario, currency, satisfaction, city_integrity, time_left, mouse_pos, mouse_click ):

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
        pygame.draw.rect(overwatch_chat, (135, 156, 232), chat_rect, 0, 5)
        pygame.draw.rect(overwatch_chat, (155, 186, 252), chat_rect, 5, 5)

        #Render texts
        name_text = self.__font.render(name, True, FONT_COLOR)
        cenario_text = self.__font.render(cenario, True, FONT_COLOR)
        money_text = self.__font.render("R$ " + str("%.2f" % round(currency, 2)), True, FONT_COLOR)
        satisfaction_text = self.__font.render(str("%.2f" % round(satisfaction, 2)) + "%", True, FONT_COLOR)
        city_integrity_text = self.__font.render(str("%.2f" % round(city_integrity, 2)) + "%", True, FONT_COLOR)
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

        #Draw measure bar and calculates psitions and sizes
        pygame.draw.rect(self.__usable_bar, RECTANGLE_COLOR, self.__usable_bar.get_rect(), 0, 25)
        pygame.draw.rect(self.__usable_bar, (255, 255, 255), self.__usable_bar.get_rect(), 8, 25)
        usable_bar_position = (self.surface.get_rect().left, self.surface.get_rect().bottom - self.__usable_bar.get_rect().height)
        measure_size = (tile_size[0] * 2, tile_size[1] * 2)
        selected_measure_size = (tile_size[0] * 2.4, tile_size[1] * 2.4)
        slot_quantity = (self.__usable_bar.get_width() // measure_size[0]) // 2
        to_center = slot_quantity - len(list_of_measures)
        division_size = measure_size[0] / 2
        
        #Blit all possible measures
        measure_font = pygame.font.SysFont(None, 15)
        for index, measure in enumerate(list_of_measures):
    
            if index > slot_quantity:
                break
            
            rescaled = pygame.transform.scale(measure.surface, measure_size)
            measure_position = (measure_size[0] + 2 * division_size) * (index + to_center // 2)
            if colisao( rescaled.get_rect(topleft=(measure_position, usable_bar_position[1] + measure_size[1] * 0.4)), pygame.Rect( mouse_pos[0], mouse_pos[1], 5, 5 ) ):
                
                #If there is collision, act accordingly
                for l_index, line in enumerate(measure.description.split('\n')):
                    chat = measure_font.render(line, True, FONT_COLOR)
                    overwatch_chat.blit( chat, (overwatch_chat.get_width() * 0.1, overwatch_chat.get_height() * (0.1 + 0.05 * (l_index + 1))))
                self.surface.blit(overwatch_chat, overwatch_chat_rect.topleft)

                if not mouse_click:
                    rescaled = pygame.transform.scale(measure.surface, selected_measure_size)
                else:
                    cursor_size[0] = measure.tiles[0]
                    cursor_size[1] = measure.tiles[1]
                    current_measures[0] = measure

            self.__usable_bar.blit(measure_font.render( measure.name, True, FONT_COLOR ), (measure_position, measure_size[1] * 0.15))
            self.__usable_bar.blit(measure_font.render( str(measure.price), True, FONT_COLOR), (measure_position, measure_size[1] * 0.3) )
            self.__usable_bar.blit( rescaled, (measure_position, measure_size[1] * 0.4)  )

        self.surface.blit(self.__usable_bar, usable_bar_position)
        self.surface.blit(player_info, player_info_rect.topleft)
        self.surface.blit(game_info, game_info_rect.topleft)
        self.surface.blit(overwatch_info, overwatch_info_rect.topleft)

class Game(Module):
    def __init__(self, screen: pygame.Surface, state:State) -> None:
        super().__init__(screen, state)

        # ---- Sizes ----
        
        screen_rect = screen.get_rect()
        screen_size = (screen_rect.width, screen_rect.height)

        # ---- Map ----

        # ---- GameObjects ----

        self.__gameobject_canvas = pygame.Surface( (screen_size[0], screen_size[1]), pygame.SRCALPHA, 32 ) 

        map_start = (screen_size[0] * 0.5, 0)
        self.__map = generate_map( './cenarios/Toquio.txt', map_size, map_start)

        self.__ocean = [ [GameObject( (1, 1), water_img, False, True, (0.1, 0.2) )] * ocean_size[1] for _ in range( ocean_size[0] ) ]
        for i in range(ocean_size[0]):
            for j in range(ocean_size[1]):
                self.__ocean[i][j].pos = (map_start[0] + 25 * 0.4 * (j - i), 
                                        map_start[1] + 25 * 0.3 * (j + i))
        
        self.__population = [Person() for _ in range(10)]
        for person in self.__population:
            person.pos = (random.randint(screen_size[0] * 0.4, screen_size[0] * 0.6), 
                          random.randint(screen_size[1] * 0.2, screen_size[1] * 0.4))

        self.__measures = []
        self.__disasters = []

        # ---- UI ----
        
        self.__player_UI = UI( self.screen, screen_size[1] * 0.185 )
        self.__show = True
        
        # ---- Camera ----

        self.__last = pygame.mouse.get_pos()
        self.camera = (0, 0)

        # ---- Game Values ----

        self.__currency = 10
        self.__satisfaction = 50
        self.__city_integrity = 100
        self.__time_left = 600
        self.__disaster_cooldown = 5
        self.__disaster_timer = 5

    def run(self, events, clock):

        time_passed = clock.tick() / 1000

        #Conditions for game to end
        lost = self.__satisfaction <= 0 or self.__city_integrity <= 0
        win = self.__time_left <= 0
        game_finished = lost or win
        if game_finished:
            #Fill in score
            self.state.score = (self.__satisfaction * self.__city_integrity * self.__currency) if win else 0
            self.state.scene = Scene.SCORE

        delta_value = (0, 0)
        current_pos = pygame.mouse.get_pos()
        mouse_click = False

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_click = True
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
                    self.state.score = 10
                    self.state.scene = Scene.SCORE
        
        #Move Camera
        screen_x = self.screen.get_width()
        screen_y = self.screen.get_height()
        new_camera_x = clamp(self.camera[0] + delta_value[0] * 10, -screen_x, screen_x )
        new_camera_y = clamp(self.camera[1] + delta_value[1] * 10, -screen_y, screen_y )
        self.camera = (new_camera_x, new_camera_y)
        #Generate mouse collision
        mouse_collision = (cursor_size[0] - 1, cursor_size[1] - 1)
        mouse_rect = pygame.Rect( current_pos[0] - mouse_collision[0] * tile_size[0] * 0.125, current_pos[1] - mouse_collision[1] * tile_size[1] * 0.125, 
                                 mouse_collision[0] * tile_size[0] * 0.25, mouse_collision[1] * tile_size[1] * 0.25 )

        #Fill map and reset values os collision
        self.screen.fill((0,0,40))
        self.__gameobject_canvas.fill((0,0,0,0))
        pygame.draw.rect( self.screen, (155,103,60), self.screen.get_rect(), 10 )

        obstacles = 0
        checked = 0
        tiles_to_exchange = []

        self.__disaster_timer -= time_passed
        if (self.__disaster_timer <= 0):
            will_there_be_disaster = disaster_master_AI( self.__time_left, 600, self.__satisfaction, self.__city_integrity, len(self.__disasters) )
            self.__disaster_timer = self.__disaster_cooldown
        else:
            will_there_be_disaster = False

        for line in self.__ocean:
            for tile in line:
                tile.draw()
                relocated_pos = ( tile.pos[0] - self.camera[0], tile.pos[1] - self.camera[1] )
                self.__gameobject_canvas.blit( tile.surface, relocated_pos )

        for l_index, line in enumerate(self.__map):
            for t_index, obj in enumerate(line):
                if obj != None:
                    obj.draw()

                    relocated_pos = ( obj.pos[0] - self.camera[0], obj.pos[1] - self.camera[1] )

                    if colisao_isometrica( obj.surface.get_rect(topleft=(relocated_pos)), mouse_rect ):
                        if obj.hover():
                            obstacles += 1
                        else:
                            tiles_to_exchange.append( (l_index, t_index) )
                        checked += 1

                    self.__gameobject_canvas.blit( obj.surface, relocated_pos )
        
        for person in self.__population:
            person.move(map_size)
            relocated_pos = ( person.pos[0] - self.camera[0], person.pos[1] - self.camera[1] )
            self.__gameobject_canvas.blit( person.surface, relocated_pos )

        for disaster in self.__disasters:
            
            disaster.draw()

            relocated_pos = ( disaster.pos[0] - self.camera[0], disaster.pos[1] - self.camera[1] )
            self.__gameobject_canvas.blit( disaster.surface, relocated_pos )

            if disaster.duration <= 0:
                self.__disasters.remove(disaster)
                del disaster
            else:
                disaster.duration -= time_passed

                damage_dealt = disaster.damage

                disaster_rect = pygame.Rect( disaster.pos[0], disaster.pos[1], disaster.area[0], disaster.area[1] )
                measures_in_effect = [] 
                for measure in self.__measures:
                    measure_rect = pygame.Rect( measure.pos[0], measure.pos[1], measure.area[0], measure.area[1] )
                    if colisao_isometrica( measure_rect, disaster_rect):
                        measures_in_effect.append(measure)
                        if disaster.safety_measures.has_key(measure):
                            damage_dealt *= (100 - disaster.safety_measures[measure]) / 100

                self.__satisfaction -= satisfaction_calculator(measures_in_effect, self.__currency, 25000)
                self.__city_integrity -= damage_dealt

        #If mouse is clicked, -no obstacle is selected, -have money, -enough space, copy measure, paste position, and replace tiles
        current_measure = current_measures[0]
        if ((current_measure != None and current_measure.price < self.__currency) 
            and (checked >= cursor_size[0] * cursor_size[1]) and (mouse_click and obstacles == 0)):
            new_measure = copy.copy(current_measure)
            new_measure.pos = self.__map[tiles_to_exchange[0][0]][tiles_to_exchange[0][1]].pos
            self.__map[tiles_to_exchange[0][0]][tiles_to_exchange[0][1]] = new_measure
            for i in range( 1, len(tiles_to_exchange) ):
                self.__map[tiles_to_exchange[i][0]][tiles_to_exchange[i][1]] = None
            self.__currency -= current_measure.price
            self.__measures.append(new_measure)
        
        if will_there_be_disaster:
            new_disaster = copy.copy( random.choice( list_of_disaster ))
            random_line = random.randint( 0, map_size[0] )
            random_column = random.randint( 0, map_size[1] )
            new_disaster.pos = (self.screen.get_width() * 0.5 + 25 * (random_column - random_line), 
                                25 * (random_column + random_line))
            self.__disasters.append(new_disaster)

        self.screen.blit(self.__gameobject_canvas, ( 0, 0 ))

        #Update values
        self.__satisfaction = clamp(self.__satisfaction, 0, 100)
        self.__city_integrity = clamp(self.__city_integrity, 0, 100)
        self.__currency = clamp(self.__currency, 0, 25000)

        #UI
        if self.__show:
            self.__player_UI.draw( self.state.name, self.state.cenario, 
                    self.__currency, self.__satisfaction, self.__city_integrity, int(self.__time_left), current_pos, mouse_click )
            self.screen.blit(self.__player_UI.surface, (0,0))

        pygame.display.flip()

        self.__currency += time_passed * random.randint(10, 50)
        self.__time_left -= time_passed