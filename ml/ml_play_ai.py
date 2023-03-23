from collections import deque
import statistics
import random

class MLPlay:
    def __init__(self, ai_name,*args,**kwargs):
        self.player_no = ai_name
        self.r_sensor_value = 0
        self.l_sensor_value = 0
        self.f_sensor_value = 0
        self.lt_sensor_value = 0
        self.rt_sensor_value = 0
        self.coordinate = deque(maxlen=50)
        self.control_list = {"left_PWM" : 0, "right_PWM" : 0}
        print(kwargs)

    def update(self, scene_info: dict, *args, **kwargs):
        """
        Generate the command according to the received scene information
        """
        if scene_info["status"] != "GAME_ALIVE":
            return "RESET"

        if len(self.coordinate) == 0:
            self.coordinate.append((scene_info["x"], scene_info["y"]))

        self.coordinate.append((scene_info["x"], scene_info["y"]))

        data = [t[1] for t in self.coordinate]
        variance = statistics.variance(data)
        self.r_sensor_value = scene_info["R_sensor"]
        self.l_sensor_value = scene_info["L_sensor"]
        self.f_sensor_value = scene_info["F_sensor"]
        self.lt_sensor_value = scene_info["L_T_sensor"]
        self.rt_sensor_value = scene_info["R_T_sensor"]

        if self.lt_sensor_value > self.rt_sensor_value:
            self.control_list["left_PWM"] = 0
            self.control_list["right_PWM"] = 255
        elif self.lt_sensor_value < self.rt_sensor_value:
            self.control_list["left_PWM"] = 255
            self.control_list["right_PWM"] = 0
        elif self.f_sensor_value > 30:
            self.control_list["left_PWM"] = 255
            self.control_list["right_PWM"] = 255

        if (variance < 1e-2 and len(self.coordinate) == self.coordinate.maxlen) or self.f_sensor_value <= 1 :
            print("restore")
            if self.lt_sensor_value > self.rt_sensor_value:
                print("left")
                self.control_list["left_PWM"] = 0
                self.control_list["right_PWM"] = -255
            else :
                print("right")
                self.control_list["left_PWM"] = -255
                self.control_list["right_PWM"] = 0
        return self.control_list

    def reset(self):
        """
        Reset the status
        """
        # print("reset ml script")
        pass
