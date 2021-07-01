from .math_function import cross_point_dot
import math

from .sensor import Sensor
import pygame
from .env import *

class Car(pygame.sprite.Sprite):
    def __init__(self, world, coordinate: tuple, car_no: int, sensor_num):
        pygame.sprite.Sprite.__init__(self)
        self.car_no = car_no  # From 0 to 5
        self.size =  (50, 40)  # car size
        self.is_completed = False
        self.end_frame = 0
        self.origin_image = pygame.transform.scale(
            pygame.image.load(path.join(IMAGE_DIR, "car_0" + str(self.car_no + 1) + ".png")),
            self.size)
        self.image = self.origin_image  # after rotate
        self.rect = self.image.get_rect()
        self.status = True
        self.sensor_R = {"coordinate":(0, 0), "distance":-1}
        self.sensor_L = {"coordinate":(0, 0), "distance":-1}
        self.sensor_R_T = {"coordinate":(0, 0), "distance":-1}
        self.sensor_L_T = {"coordinate":(0, 0), "distance":-1}
        self.sensor_F = {"coordinate":(0, 0), "distance":-1}
        self.L_PWM = 0
        self.R_PWM = 0
        self.rect.center = (0, 0)  # pygame
        self.x, self.y = coordinate
        self.body = world.CreateDynamicBody(position=coordinate)
        self.box = self.body.CreatePolygonFixture(box=(1.13, 1.13), density=1, friction=0.1, restitution=0.3)
        self.sensor = Sensor(world, self.body, sensor_num)
        self.check_point = 0

    def update(self, commands):
        self.image = pygame.transform.rotate(self.origin_image, (self.body.angle * 180 / math.pi) % 360)
        self.rect = self.image.get_rect()
        if self.status and commands != None:
            if commands[0]['right_PWM'] > 255:
                self.R_PWM = 255
            elif commands[0]['right_PWM'] < -255:
                self.R_PWM = -255
            else:
                self.R_PWM = commands[0]['right_PWM']
            if commands[0]['left_PWM'] > 255:
                self.L_PWM = 255
            elif commands[0]['left_PWM'] < -255:
                self.L_PWM = -255
            else:
                self.L_PWM = commands[0]['left_PWM']
            self.left_move(self.L_PWM)
            self.right_move(self.R_PWM)
        else:
            self.body.linearVelocity = (0, 0)


    def detect_distance(self, frame, walls):
        sensor_value = self.sensor.update(frame, walls)
        self.sensor_R = sensor_value["right_value"]
        self.sensor_L = sensor_value["left_value"]
        self.sensor_R_T = sensor_value["right_top_value"]
        self.sensor_L_T = sensor_value["left_top_value"]
        self.sensor_F = sensor_value["front_value"]

    def left_move(self, pwm: int):
        if pwm <0:
            self.sensor.sensor_left.linearVelocity = self.body.GetWorldVector(localVector=(0, -(abs(pwm) ** 0.5)))
        else:
            self.sensor.sensor_left.linearVelocity =self.body.GetWorldVector(localVector = (0,pwm**0.5))

    def right_move(self, pwm: int):
        if pwm <0:
            self.sensor.sensor_right.linearVelocity = self.body.GetWorldVector(localVector=(0, -(abs(pwm) ** 0.5)))
        else:
            self.sensor.sensor_right.linearVelocity =self.body.GetWorldVector(localVector = (0,pwm**0.5))

    def keep_in_screen(self):
        pass

    def get_info(self):
        self.car_info = {"id": self.car_no,
                         "status":self.status,
                         "size": self.size,  # pygame
                         "topleft": self.rect.topleft,  # pygame
                         "center":self.rect.center,
                         "coordinate":self.body.position,
                         "angle": self.body.angle,  # Box2D
                         "r_sensor_value": self.sensor_R["distance"],
                         "l_sensor_value": self.sensor_L["distance"],
                         "r_t_sensor_value": self.sensor_R_T["distance"],
                         "l_t_sensor_value": self.sensor_L_T["distance"],
                         "f_sensor_value": self.sensor_F["distance"],
                         "L_PWM": self.L_PWM,
                         "R_PWM":self.R_PWM,
                         "end_frame":self.end_frame,
                         }
        return self.car_info
