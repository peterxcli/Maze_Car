import time
import Box2D

from .end_point import End_point, Check_point
from .maze_wall import Wall
from .tilemap import Map, Camera
from .maze_imformation import Normal_Maze_Size, Normal_Maze_Map
from .car import Car
from .gameMode import GameMode
from .env import *
import pygame

class MazeMode(GameMode):
    def __init__(self, user_num: int, maze_no, time, sound_controller):
        super(MazeMode, self).__init__()
        self.game_end_time = time  # int, decide how many second the game will end even some users don't finish game
        self.ranked_user = []  # pygame.sprite car
        self.ranked_score = {"1P": 0, "2P": 0, "3P": 0, "4P": 0, "5P": 0, "6P": 0}  # 積分
        pygame.font.init()
        self.status = "GAME_PASS"
        self.is_end = False
        self.result = []
        self.x = 0
        self.maze_id = maze_no - 1
        self.map_file = NORMAL_MAZE_MAPS[self.maze_id]
        self.size = 1
        self.start_pos = (22, 3)
        self.wall_info = []
        '''set group'''
        self.car_info = []
        self.cars = pygame.sprite.Group()
        self.worlds = []
        self.all_sprites = pygame.sprite.Group()
        self._init_world(user_num)
        self._init_car()
        # self._init_maze(self.maze_id)
        self.eliminated_user = []
        self.user_check_points = []
        self.new()
        # self.pygame_point = [0, self.map.tileHeight]  # Box2D to Pygame
        # self.pygame_point = [TILE_LEFTTOP[0]/-PPM, TILE_LEFTTOP[1]/PPM]  # Box2D to Pygame
        self.pygame_point = [0,0]  # Box2D to Pygame

        '''sound'''
        self.sound_controller = sound_controller

        '''image'''
        self.info = pygame.image.load(path.join(IMAGE_DIR, info_image))

    def update_sprite(self, command):
        '''update the model of game,call this fuction per frame'''
        self.car_info = []
        self.frame += 1
        self.handle_event()
        self._is_game_end()
        self.command = command
        # self.pygame_point = [self.car.body.position[0] - (TILE_LEFTTOP[0] + TILE_WIDTH) / 2 / PPM,
        #                      self.car.body.position[1] + HEIGHT / 2 / PPM]
        self.limit_pygame_screen()
        for car in self.cars:
            car.update(command["ml_" + str(car.car_no + 1) + "P"])
            car.rect.center = self.trnsfer_box2d_to_pygame(car.body.position)
            self.car_info.append(car.get_info())
            # self._is_car_arrive_end(car)
            car.detect_distance(self.frame, self.wall_info)
        self.all_sprites.update()
        for sprite in self.all_sprites:
            sprite.rect.x, sprite.rect.y = self.trnsfer_box2d_to_pygame((sprite.x + TILESIZE/2/PPM, -sprite.y - TILESIZE/2/PPM))
            # print(sprite.rect.center)
        for world in self.worlds:
            world.Step(TIME_STEP, 10, 10)
            world.ClearForces()
        if self.is_end:
            self.running = False

    def trnsfer_box2d_to_pygame(self, coordinate):
        '''
        :param coordinate: vertice of body of box2d object
        :return: center of pygame rect
        '''
        return ((coordinate[0]- self.pygame_point[0]) * PPM, (self.pygame_point[1] - coordinate[1])*PPM)

    def limit_pygame_screen(self):
        self.pygame_point = [self.car.body.position[0] - (TILE_LEFTTOP[0] + TILE_WIDTH) / 2 / PPM,
                             self.car.body.position[1] + HEIGHT / 2 / PPM]
        if self.pygame_point[1] > 0:
            self.pygame_point[1] = 0
        elif self.pygame_point[1] < TILE_HEIGHT/PPM-self.map.tileHeight:
            self.pygame_point[1] = TILE_HEIGHT/PPM-self.map.tileHeight
        else:
            pass
        if self.pygame_point[0] >self.map.tileWidth-TILE_WIDTH/PPM:
            self.pygame_point[0] = self.map.tileWidth-TILE_WIDTH/PPM
        elif self.pygame_point[0] < 0:
            self.pygame_point[0] = 0
        else:
            pass
    def new(self):
        self.load_data()
        self.walls = pygame.sprite.Group()
        self.get_wall_info()
        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                if tile == "1":
                    for world in self.worlds:
                        Wall(self, (col + (TILE_LEFTTOP[0] / TILESIZE), row + (TILE_LEFTTOP[1] / TILESIZE)), world,
                                  len(self.map.data))
                elif tile == "E":
                    self.end_point = End_point(self, (col + (TILE_LEFTTOP[0] / TILESIZE), row + (TILE_LEFTTOP[1] / TILESIZE)))
                elif tile == "C":
                    Check_point(self, (col + (TILE_LEFTTOP[0] / TILESIZE), row + (TILE_LEFTTOP[1] / TILESIZE)))

        self.camera = Camera(self.map.width, self.map.height)
        pass

    def get_wall_info(self):
        wall_tiles = []
        for row, tiles in enumerate(self.map.data):
            col = 0
            first_tile = -1
            last_tile = -1
            while col < (len(tiles)):
                if tiles[col] == "1":
                    if first_tile == -1:
                        first_tile = col
                        if col == len(tiles) -1:
                            last_tile = col
                            self.wall_vertices((first_tile, row), (last_tile, row))
                            first_tile = -1
                            col += 1
                        else:
                            col += 1
                    elif col == len(tiles) -1:
                        last_tile = col
                        self.wall_vertices((first_tile, row), (last_tile, row))
                        first_tile = -1
                        col += 1
                    else:
                        col += 1
                else:
                    if first_tile != -1:
                        last_tile = col - 1
                        self.wall_vertices((first_tile, row), (last_tile, row))
                        first_tile = -1
                        col += 1
                    else:
                        col += 1

    def wall_vertices(self, first_tile, last_tile):
        first_tilex = first_tile[0]+ TILESIZE/ (2*PPM) + 1
        first_tiley = GRIDHEIGHT + TILE_LEFTTOP[1] / PPM - first_tile[1] - TILESIZE/ (2*PPM) - 1
        last_tilex = last_tile[0]+ TILESIZE/ (2*PPM) + 1
        last_tiley = GRIDHEIGHT + TILE_LEFTTOP[1] / PPM - last_tile[1] - TILESIZE/ (2*PPM) - 1
        r = TILESIZE/ (2*PPM)
        vertices = [(first_tilex - r, first_tiley + r),
                    (last_tilex + r, last_tiley + r),
                    (last_tilex + r, last_tiley - r),
                    (first_tilex - r, first_tiley -r)
                    ] #Box2D
        self.wall_info.append([vertices[0],vertices[1]])
        self.wall_info.append([vertices[2],vertices[1]])
        self.wall_info.append([vertices[3],vertices[0]])
        self.wall_info.append([vertices[2],vertices[3]])
        return vertices
        pass

    def load_data(self):
        game_folder = path.dirname(__file__)
        map_folder = path.join(path.dirname(__file__), "map")
        self.map = Map(path.join(map_folder, self.map_file))
        # self.map = Map(path.join(map_folder, MAZE_TEST))
        pass

    def detect_collision(self):
        super(MazeMode, self).detect_collision()
        pass

    def _print_result(self):
        if self.is_end and self.x == 0:
            for user in self.ranked_user:
                self.result.append(str(user.car_no + 1) + "P:" + str(user.end_frame) + "frame")
                self.ranked_score[str(user.car_no + 1) + "P"] = user.score
            print("score:", self.ranked_score)
            self.x += 1
            print(self.result)
        pass

    def _init_world(self, user_no: int):
        for i in range(user_no):
            world = Box2D.b2.world(gravity=(0, 0), doSleep=True, CollideConnected=False)
            self.worlds.append(world)

    def _init_car(self):
        self.start_pos = (29, -30)
        for world in self.worlds:
            self.car = Car(world, self.start_pos, self.worlds.index(world), self.size)
            self.cars.add(self.car)
            self.car_info.append(self.car.get_info())

    def _init_maze(self, maze_no):
        for world in self.worlds:
            for wall in Normal_Maze_Map[maze_no]:
                wall_bottom = world.CreateKinematicBody(position=(0, 0), linearVelocity=(0, 0))
                box = wall_bottom.CreatePolygonFixture(vertices=wall)
        pass

    def _is_game_end(self):
        if self.frame > FPS * self.game_end_time or len(self.eliminated_user) == len(self.cars):
            print("game end")
            for car in self.cars:
                if car not in self.eliminated_user and car.status:
                    car.end_time = self.frame
                    self.eliminated_user.append(car)
                    self.user_check_points.append(car.check_point)
                    car.status = False
            self.is_end = True
            self.rank()
            self._print_result()
            self.status = "GAME OVER"

    def draw_bg(self):
        '''show the background and imformation on screen,call this fuction per frame'''
        super(MazeMode, self).draw_bg()
        self.screen.fill(BLACK)


    def drawWorld(self):
        '''show all cars and lanes on screen,call this fuction per frame'''
        super(MazeMode, self).drawWorld()
        for wall in self.walls:
            vertices = [(wall.body.transform * v) for v in wall.box.shape.vertices]
            vertices = [self.trnsfer_box2d_to_pygame(v) for v in vertices]
            pygame.draw.polygon(self.screen, WHITE, vertices)

        # self.all_sprites.draw(self.screen)
        self.cars.draw(self.screen)
        '''色塊'''
        pygame.draw.rect(self.screen, BLACK, pygame.Rect(0, 0, TILE_LEFTTOP[0], HEIGHT))
        pygame.draw.rect(self.screen, BLACK, pygame.Rect(0, 0, WIDTH, TILE_LEFTTOP[1]))
        pygame.draw.rect(self.screen, BLACK, pygame.Rect(TILE_LEFTTOP[0]+TILE_WIDTH, 0, WIDTH-TILE_LEFTTOP[0]-TILE_WIDTH, HEIGHT))
        pygame.draw.rect(self.screen, BLACK, pygame.Rect(0, TILE_LEFTTOP[1]+TILE_HEIGHT, WIDTH, HEIGHT - TILE_LEFTTOP[1]-TILE_HEIGHT))
        self.screen.blit(self.info, pygame.Rect(507, 20, 306, 480))


        try:
            self.screen.blit(self.end_point.image, self.end_point.rect)
        except Exception:
            pass
        if self.is_end == False:
            self.draw_time(self.frame)
        '''畫出每台車子的資訊'''
        self._draw_user_imformation()

        # self.draw_grid()


    def _draw_user_imformation(self):
        for i in range(6):
            for car in self.cars:
                if car.car_no == i:
                    if i % 2 == 0:
                        if car.status:
                            self.draw_information(self.screen, YELLOW, "L:" + str(car.sensor_L) + "cm", 600,
                                                  178 + 20 + 94 * i / 2)
                            self.draw_information(self.screen, RED, "F:" + str(car.sensor_F) + "cm", 600,
                                                  178 + 40 + 94 * i / 2)
                            self.draw_information(self.screen, LIGHT_BLUE, "R:" + str(car.sensor_R) + "cm", 600,
                                                  178 + 60 + 94 * i / 2)
                        else:
                            self.draw_information(self.screen, WHITE, str(car.end_frame) + "frame",
                                                  600, 178 + 40 + 94 * (i // 2))

                    else:
                        if car.status:
                            self.draw_information(self.screen, YELLOW, "L:" + str(car.sensor_L) + "cm", 730,
                                                  178 + 20 + 94 * (i // 2))
                            self.draw_information(self.screen, RED, "F:" + str(car.sensor_F) + "cm", 730,
                                                  178 + 40 + 94 * (i // 2))
                            self.draw_information(self.screen, LIGHT_BLUE, "R:" + str(car.sensor_R) + "cm", 730,
                                                  178 + 60 + 94 * (i // 2))
                        else:
                            self.draw_information(self.screen, WHITE, str(car.end_frame) + "frame",
                                                  730, 178 + 40 + 94 * (i // 2))

    def rank(self):
        while len(self.eliminated_user) > 0:
            for car in self.eliminated_user:
                if car.is_completed:
                    self.ranked_user.append(car)
                    self.eliminated_user.remove(car)
                else:
                    if car.check_point == max(self.user_check_points):
                        self.ranked_user.append(car)
                        self.user_check_points.remove(car.check_point)
                        self.eliminated_user.remove(car)
        for i in range(len(self.ranked_user)):
            if self.ranked_user[i].end_frame == self.ranked_user[i - 1].end_frame:
                if i == 0:
                    self.ranked_user[i].score = 6
                else:
                    for j in range(1, i + 1):
                        if self.ranked_user[i - j].end_frame == self.ranked_user[i].end_frame:
                            if i == j:
                                self.ranked_user[i].score = 6
                            else:
                                pass
                            pass
                        else:
                            self.ranked_user[i].score = 6 - (i - j + 1)
                            break
            else:
                self.ranked_user[i].score = 6 - i

    def draw_grid(self):
        for x in range(TILE_LEFTTOP[0], TILE_WIDTH + TILE_LEFTTOP[0], TILESIZE):
            pygame.draw.line(self.screen, GREY, (x, TILE_LEFTTOP[1]), (x, TILE_HEIGHT + TILE_LEFTTOP[1]))
        for y in range(TILE_LEFTTOP[1], TILE_HEIGHT + TILE_LEFTTOP[1], TILESIZE):
            pygame.draw.line(self.screen, GREY, (TILE_LEFTTOP[0], y), (TILE_WIDTH + TILE_LEFTTOP[0], y))