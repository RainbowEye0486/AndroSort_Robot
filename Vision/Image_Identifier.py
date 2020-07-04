import cv2
import numpy as np
import math
import time
from threading import Thread
import json
import os
import sys
from Strategy import challenge_3 as ch3
from Strategy import challenge_2 as ch2
from Strategy import challenge_1 as ch1

camera_switch = 1  # 哪一個相機
#  紀錄參數用
if camera_switch == 0:
    fpath = os.path.join(os.path.dirname(__file__), 'param.json')
else:
    fpath = os.path.join(os.path.dirname(__file__), 'param2.json')

with open(fpath, 'r') as file_in:
    jf = json.load(file_in)
font = cv2.FONT_HERSHEY_SIMPLEX
cap = None
#  需要調整參數
challenge_bit = 3
camera_num = 0
robot_height = 45
field_height = 268
color_upper_clipper = 850  # 調整面積的讀取區間
color_lower_clipper = 100
#  遮色片參數
mask = False
once_open_mask = False
threshold = 20

# don't care config
point_show = False  # 場地標點
error_open = True  # 如果標好相機投影點將會開啟
frame_counter = 0
exit_bit = 0

#  紀錄特殊點位置
ball_pos_last = [0, 0]
ball_pos_now = [0, 0]
ball_speed = 0
ball_dir = [0, 0]

middle = jf["special_point"]["middle"]
camera_project = jf["special_point"]["camera_project"]
penalty_pos = jf["special_point"]["penalty_pos"]
FB_pos = list()
FK_pos = list()
PK_pos = list()
# mark special corner point of play field
field_pos = jf["special_point"]["field_pos"]
#  紀錄色塊的中心點
enemy_pos = set()
our_pos = set()
color2_pos = set()
color1_pos = set()
color3_pos = set()
#  紀錄不同區域的同一種顏色 取範圍

current_window = 'camera'
mask_frame = None
mask_color = ''

our_lower = np.array(jf["color_patch"]["our_lower"])
our_upper = np.array(jf["color_patch"]["our_upper"])
enemy_lower = np.array(jf["color_patch"]["enemy_lower"])
enemy_upper = np.array(jf["color_patch"]["enemy_upper"])
color1_lower = np.array(jf["color_patch"]["color1_lower"])
color1_upper = np.array(jf["color_patch"]["color1_upper"])
color2_lower = np.array(jf["color_patch"]["color2_lower"])
color2_upper = np.array(jf["color_patch"]["color2_upper"])
color3_lower = np.array(jf["color_patch"]["color3_lower"])
color3_upper = np.array(jf["color_patch"]["color3_upper"])
ball_lower = np.array(jf["color_patch"]["ball_lower"])
ball_upper = np.array(jf["color_patch"]["ball_upper"])
pick_time = [0, 0, 0, 0, 0, 0]  # 紀錄顏色的取樣次數，超過五次之後從頭計算

field_data = list()
our_data = [[], [], []]
our_dir = [[], [], []]
enemy_data = [[], [], []]
field_data.append(field_pos)


def return_motion():  # 回傳所有可移動物體的位置
    motion = [our_data, enemy_data]
    return motion


def return_field():
    print(field_data)
    return field_data


def get_distance(start, end):
    distance = math.pow((start[0] - end[0]), 2) + math.pow((start[1] - end[1]), 2)
    distance = math.sqrt(distance)
    return distance


def error_correct(i):
    oasis = [i[0], i[1]]
    oasis[0] = int(camera_project[0] + (i[0] - camera_project[0]) * (1 - (robot_height / field_height)))
    oasis[1] = int(camera_project[1] + (i[1] - camera_project[1]) * (1 - (robot_height / field_height)))
    return oasis


def set_field():
    global point_show
    point_show = ~point_show
    if ~point_show:
        jf["special_point"]["field_pos"] = field_pos
        jf["special_point"]["middle"] = middle
        with open(fpath, 'w') as file_out:
            file_out.write(json.dumps(jf))
    print("set 12 corner")
    cv2.setMouseCallback('camera_RGB', pick_field)


def set_mask():
    global mask
    if ~mask:
        print("open mask")
    else:
        cv2.destroyWindow(current_window)
    mask = ~mask


def set_correct():
    print("pick camera projection")
    cv2.setMouseCallback('camera_RGB', pick_error)


def set_our():
    global current_window, once_open_mask, mask_color
    print("please click our team color")
    current_window = 'our_mask'
    cv2.setMouseCallback('camera_RGB', pick_color_our_main)
    once_open_mask = True
    mask_color = 'o'


def set_enemy():
    global current_window, once_open_mask, mask_color
    print("please click enemy team color")
    current_window = 'enemy_mask'
    cv2.setMouseCallback('camera_RGB', pick_color_enemy_main)
    once_open_mask = True
    mask_color = 'e'


def set_color1():
    global current_window, once_open_mask, mask_color
    print("please click robot 1 color")
    current_window = 'color1_mask'
    cv2.setMouseCallback('camera_RGB', pick_color_one)
    once_open_mask = True
    mask_color = '1'


def set_color2():
    global current_window, once_open_mask, mask_color
    print("please click robot 2 color")
    current_window = 'color2_mask'
    cv2.setMouseCallback('camera_RGB', pick_color_two)
    once_open_mask = True
    mask_color = '2'


def set_color3():
    global current_window, once_open_mask, mask_color
    print("please click robot 3 color")
    current_window = 'color3_mask'
    cv2.setMouseCallback('camera_RGB', pick_color_three)
    once_open_mask = True
    mask_color = '3'


def set_ball():
    global current_window, once_open_mask, mask_color
    print("please click ball")
    current_window = 'ball_mask'
    cv2.setMouseCallback('camera_RGB', pick_color_ball)
    once_open_mask = True
    mask_color = 'b'


def pick_error(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global camera_project
        jf["special_point"]["camera_project"] = [x, y]
        with open(fpath, 'w') as file_out:
            file_out.write(json.dumps(jf))
        print("camera projection point", jf["special_point"]["camera_project"])
        global error_open
        error_open = True


def pick_field(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print('(', x, ',', y, '), ')
        if len(jf["special_point"]["field_pos"]) < 12:
            jf["special_point"]["field_pos"].append([x, y])
            if len(jf["special_point"]["field_pos"]) == 8:  # 標出中心點
                middle[0] = int((jf["special_point"]["field_pos"][0][0] + jf["special_point"]["field_pos"][1][0]
                                 + jf["special_point"]["field_pos"][6][0] + jf["special_point"]["field_pos"][7][0]) / 4)
                middle[1] = int((jf["special_point"]["field_pos"][0][1] + jf["special_point"]["field_pos"][1][1]
                                 + jf["special_point"]["field_pos"][6][1] + jf["special_point"]["field_pos"][7][1]) / 4)
                jf["special_point"]["middle"] = middle
                print(middle)
        else:
            if len(penalty_pos) < 4:
                jf["special_point"]["penalty_pos"].append([x, y])
            else:
                if len(FB_pos) < 4:
                    FB_pos.append([x, y])
                else:
                    if len(FK_pos) < 2:
                        FK_pos.append([x, y])
                    else:
                        if len(PK_pos) < 2:
                            PK_pos.append([x, y])
        with open(fpath, 'w') as file_out:
            file_out.write(json.dumps(jf))
    elif event == cv2.EVENT_MBUTTONDOWN:
        if len(jf["special_point"]["field_pos"]) < 12:
            jf["special_point"]["field_pos"].pop()
        elif len(jf["special_point"]["field_pos"]) == 0:
            print("empty list")
        else:
            if len(jf["special_point"]["penalty_pos"]) < 4:
                if len(jf["special_point"]["penalty_pos"]) == 0:
                    jf["special_point"]["field_pos"].pop()
                else:
                    jf["special_point"]["penalty_pos"].pop()
            else:
                if len(FB_pos) < 4:
                    if len(FB_pos) == 0:
                        jf["special_point"]["penalty_pos"].pop()
                    else:
                        FB_pos.pop()
                else:
                    if len(FK_pos) < 2:
                        if len(FK_pos) == 0:
                            FB_pos.pop()
                        else:
                            FK_pos.pop()
                    else:
                        if len(PK_pos) < 2:
                            if len(PK_pos) == 0:
                                FK_pos.pop()
                            else:
                                PK_pos.pop()
        with open(fpath, 'w') as file_out:
            file_out.write(json.dumps(jf))


def pick_color_our_main(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global our_upper, our_lower
        pick_time[0] += 1
        pixel = frame[y, x]
        if pick_time[0] < 6:
            upper = [int(max(pixel[0] + threshold, our_upper[0])), int(max(pixel[1] + threshold, our_upper[1])),
                     int(max(pixel[2] + threshold, our_upper[2]))]
            lower = [int(min(pixel[0] - threshold, our_lower[0])), int(min(pixel[1] - threshold, our_lower[1])),
                     int(min(pixel[2] - threshold, our_lower[2]))]
        else:
            upper = [int(pixel[0] + threshold), int(pixel[1] + threshold), int(pixel[2] + threshold)]
            lower = [int(pixel[0] - threshold), int(pixel[1] - threshold), int(pixel[2] - threshold)]
            pick_time[0] = 0
        jf["color_patch"]["our_upper"] = upper
        jf["color_patch"]["our_lower"] = lower
        with open(fpath, 'w') as file_out:
            file_out.write(json.dumps(jf))
        our_upper = np.array(upper)
        our_lower = np.array(lower)
        print("now our main", our_lower, our_upper, pick_time[0])


def pick_color_enemy_main(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global enemy_upper, enemy_lower
        pick_time[1] += 1
        pixel = frame[y, x]
        if pick_time[1] < 6:
            upper = [int(max(pixel[0] + threshold, enemy_upper[0])), int(max(pixel[1] + threshold, enemy_upper[1])),
                     int(max(pixel[2] + threshold, enemy_upper[2]))]
            lower = [int(min(pixel[0] - threshold, enemy_lower[0])), int(min(pixel[1] - threshold, enemy_lower[1])),
                     int(min(pixel[2] - threshold, enemy_lower[2]))]
        else:
            upper = [int(pixel[0] + threshold), int(pixel[1] + threshold), int(pixel[2] + threshold)]
            lower = [int(pixel[0] - threshold), int(pixel[1] - threshold), int(pixel[2] - threshold)]
            pick_time[1] = 0
        jf["color_patch"]["enemy_upper"] = upper
        jf["color_patch"]["enemy_lower"] = lower
        with open(fpath, 'w') as file_out:
            file_out.write(json.dumps(jf))
        enemy_upper = np.array(upper)
        enemy_lower = np.array(lower)
        print("now enemy main", enemy_upper, enemy_lower, pick_time[1])


def pick_color_one(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global color1_upper, color1_lower
        pick_time[2] += 1
        pixel = frame[y, x]
        if pick_time[2] < 6:
            upper = [int(max(pixel[0] + threshold, color1_upper[0])), int(max(pixel[1] + threshold, color1_upper[1])),
                     int(max(pixel[2] + threshold, color1_upper[2]))]
            lower = [int(min(pixel[0] - threshold, color1_lower[0])), int(min(pixel[1] - threshold, color1_lower[1])),
                     int(min(pixel[2] - threshold, color1_lower[2]))]
        else:
            upper = [int(pixel[0] + threshold), int(pixel[1] + threshold), int(pixel[2] + threshold)]
            lower = [int(pixel[0] - threshold), int(pixel[1] - threshold), int(pixel[2] - threshold)]
            pick_time[2] = 0
        jf["color_patch"]["color1_upper"] = upper
        jf["color_patch"]["color1_lower"] = lower
        with open(fpath, 'w') as file_out:
            file_out.write(json.dumps(jf))
        color1_upper = np.array(upper)
        color1_lower = np.array(lower)
        print("now robot 1", color1_upper, color1_lower, pick_time[2])


def pick_color_two(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global color2_upper, color2_lower
        pick_time[3] += 1
        pixel = frame[y, x]
        if pick_time[3] < 6:
            upper = [int(max(pixel[0] + threshold, color2_upper[0])), int(max(pixel[1] + threshold, color2_upper[1])),
                     int(max(pixel[2] + threshold, color2_upper[2]))]
            lower = [int(min(pixel[0] - threshold, color2_lower[0])), int(min(pixel[1] - threshold, color2_lower[1])),
                     int(min(pixel[2] - threshold, color2_lower[2]))]
        else:
            upper = [int(pixel[0] + threshold), int(pixel[1] + threshold), int(pixel[2] + threshold)]
            lower = [int(pixel[0] - threshold), int(pixel[1] - threshold), int(pixel[2] - threshold)]
            pick_time[3] = 0
        jf["color_patch"]["color2_upper"] = upper
        jf["color_patch"]["color2_lower"] = lower
        with open(fpath, 'w') as file_out:
            file_out.write(json.dumps(jf))
        color2_upper = np.array(upper)
        color2_lower = np.array(lower)
        print("now robot 2", color2_upper, color2_lower, pick_time[3])
        mask_color = '2'


def pick_color_three(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global color3_upper, color3_lower
        pick_time[4] += 1
        pixel = frame[y, x]
        if pick_time[4] < 6:
            upper = [int(max(pixel[0] + threshold, color3_upper[0])), int(max(pixel[1] + threshold, color3_upper[1])),
                     int(max(pixel[2] + threshold, color3_upper[2]))]
            lower = [int(min(pixel[0] - threshold, color3_lower[0])), int(min(pixel[1] - threshold, color3_lower[1])),
                     int(min(pixel[2] - threshold, color3_lower[2]))]
        else:
            upper = [int(pixel[0] + threshold), int(pixel[1] + threshold), int(pixel[2] + threshold)]
            lower = [int(pixel[0] - threshold), int(pixel[1] - threshold), int(pixel[2] - threshold)]
            pick_time[4] = 0
        jf["color_patch"]["color3_upper"] = upper
        jf["color_patch"]["color3_lower"] = lower
        with open(fpath, 'w') as file_out:
            file_out.write(json.dumps(jf))
        color3_upper = np.array(upper)
        color3_lower = np.array(lower)
        print("now robot 3", color3_upper, color3_lower, pick_time[4])


def pick_color_ball(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global ball_upper, ball_lower
        pick_time[5] += 1
        pixel = frame[y, x]
        if pick_time[5] < 6:
            upper = [int(max(pixel[0] + threshold + 10, ball_upper[0])),
                     int(max(pixel[1] + threshold + 10, ball_upper[1])),
                     int(max(pixel[2] + threshold + 10, ball_upper[2]))]
            lower = [int(min(pixel[0] - threshold - 10, ball_lower[0])),
                     int(min(pixel[1] - threshold - 10, ball_lower[1])),
                     int(min(pixel[2] - threshold - 10, ball_lower[2]))]
        else:
            upper = [int(pixel[0] + threshold + 10), int(pixel[1] + threshold + 10), int(pixel[2] + threshold + 10)]
            lower = [int(pixel[0] - threshold - 10), int(pixel[1] - threshold - 10), int(pixel[2] - threshold - 10)]
            pick_time[5] = 0
        jf["color_patch"]["ball_upper"] = upper
        jf["color_patch"]["ball_lower"] = lower
        with open(fpath, 'w') as file_out:
            file_out.write(json.dumps(jf))
        ball_upper = np.array(upper)
        ball_lower = np.array(lower)
        print("now ball", ball_upper, ball_lower, pick_time[5])


def thread_our():
    # #####################--our--######################################################
    global mask_frame
    our_mask = cv2.inRange(frame, our_lower, our_upper)
    # our_mask = cv2.medianBlur(our_mask, FILTER_KERNEL)  # medium filter
    contours, hierarchy = cv2.findContours(our_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for cnt in contours:
        rect = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rect)  # cv.boxPoints(rect) for OpenCV 3.x 获取最小外接矩形的4个顶点
        box = np.int0(box)
        x = int(rect[0][0])
        y = int(rect[0][1])
        if (cv2.contourArea(cnt) < color_lower_clipper) | (cv2.contourArea(cnt) > color_upper_clipper):  # 面積過小
            continue
        our_pos.add((x, y))
        cv2.circle(show, (x, y), 1, (252, 255, 255), 1)
        cv2.circle(show, (x, y), 30, (252, 255, 255), 1)  # patten range
        cv2.drawContours(show, [box], -1, (25, 40, 220), 1)
        cv2.putText(show, "our", (x, y - 5), font, 0.7, (25, 40, 220), 1)
    if mask_color == 'o':
        mask_frame = our_mask


def thread_enemy():
    # #####################--enemy--######################################################
    global mask_frame
    enemy_mask = cv2.inRange(frame, enemy_lower, enemy_upper)
    contours, hierarchy = cv2.findContours(enemy_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for cnt in contours:
        rect = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rect)  # cv.boxPoints(rect) for OpenCV 3.x 获取最小外接矩形的4个顶点
        box = np.int0(box)
        x = int(rect[0][0])
        y = int(rect[0][1])
        if (cv2.contourArea(cnt) < color_lower_clipper) | (cv2.contourArea(cnt) > color_upper_clipper):  # 面積過小
            continue
        enemy_pos.add((x, y))
        cv2.circle(show, (x, y), 1, (252, 255, 255), 1)
        cv2.circle(show, (x, y), 30, (252, 255, 255), 1)  # patten range
        cv2.drawContours(show, [box], -1, (255, 155, 0), 1)
        cv2.putText(show, "enemy", (x, y - 5), font, 0.7, (255, 155, 0), 1)
    if mask_color == 'e':
        mask_frame = enemy_mask


def thread_color1():
    # #####################--color1--#####################################################
    global mask_frame
    color1_mask = cv2.inRange(frame, color1_lower, color1_upper)
    # color1_mask = cv2.medianBlur(color1_mask, FILTER_KERNEL)  # medium filter
    contours, hierarchy = cv2.findContours(color1_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for cnt in contours:
        rect = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rect)  # cv.boxPoints(rect) for OpenCV 3.x 获取最小外接矩形的4个顶点
        box = np.int0(box)
        x = int(rect[0][0])
        y = int(rect[0][1])
        if (cv2.contourArea(cnt) < color_lower_clipper) | (cv2.contourArea(cnt) > color_upper_clipper):  # 面積過小
            continue
        color1_pos.add((x, y))
        cv2.circle(show, (x, y), 1, (252, 255, 255), 1)
        cv2.drawContours(show, [box], -1, (45, 265, 230), 1)
        cv2.putText(show, "color1", (x, y - 5), font, 0.7, (45, 165, 230), 1)
    if mask_color == '1':
        mask_frame = color1_mask


def thread_color2():
    # #####################--color2--#####################################################
    global mask_frame
    color2_mask = cv2.inRange(frame, color2_lower, color2_upper)
    # color2_mask = cv2.medianBlur(color2_mask, FILTER_KERNEL)  # medium filter
    contours, hierarchy = cv2.findContours(color2_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for cnt in contours:
        rect = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rect)  # cv.boxPoints(rect) for OpenCV 3.x 获取最小外接矩形的4个顶点
        box = np.int0(box)
        x = int(rect[0][0])
        y = int(rect[0][1])
        if (cv2.contourArea(cnt) < color_lower_clipper) | (cv2.contourArea(cnt) > color_upper_clipper):  # 面積過小
            continue
        color2_pos.add((x, y))
        cv2.circle(show, (x, y), 1, (252, 255, 255), 1)
        cv2.drawContours(show, [box], -1, (150, 205, 0), 1)
        cv2.putText(show, "color2", (x, y - 5), font, 0.7, (150, 205, 0), 1)
    if mask_color == '2':
        mask_frame = color2_mask


def thread_color3():
    # #####################--color3--#####################################################
    global mask_frame
    color3_mask = cv2.inRange(frame, color3_lower, color3_upper)
    # color3_mask = cv2.medianBlur(color3_mask, FILTER_KERNEL)  # medium filter
    contours, hierarchy = cv2.findContours(color3_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for cnt in contours:
        rect = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rect)  # cv.boxPoints(rect) for OpenCV 3.x 获取最小外接矩形的4个顶点
        box = np.int0(box)
        x = int(rect[0][0])
        y = int(rect[0][1])
        if (cv2.contourArea(cnt) < color_lower_clipper) | (cv2.contourArea(cnt) > color_upper_clipper):  # 面積過小
            continue
        color3_pos.add((x, y))
        cv2.circle(show, (x, y), 1, (252, 255, 255), 1)
        cv2.drawContours(show, [box], -1, (220, 50, 200), 1)
        cv2.putText(show, "color3", (x, y - 5), font, 0.7, (220, 50, 200), 1)
    if mask_color == '3':
        mask_frame = color3_mask


def thread_ball():
    # ######################--BALL--#####################################################
    global ball_pos_now, mask_frame
    ball_mask = cv2.inRange(frame, ball_lower, ball_upper)
    # ball_mask = cv2.medianBlur(ball_mask, FILTER_KERNEL)  # medium filter
    contours, hierarchy = cv2.findContours(ball_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for cnt in contours:
        rect = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rect)  # cv.boxPoints(rect) for OpenCV 3.x 获取最小外接矩形的4个顶点
        box = np.int0(box)
        x = int(rect[0][0])
        y = int(rect[0][1])
        if (cv2.contourArea(cnt) < 30) | (cv2.contourArea(cnt) > color_upper_clipper):  # 面積過小
            continue
        elif (x > field_pos[1][0]) | (x < field_pos[0][0]) | (y > field_pos[7][1]) | (y < field_pos[0][1]):
            continue
        cv2.circle(show, (x, y), 1, (252, 255, 255), 1)
        #  speed of ball
        ball_pos_now = [x, y]
        cv2.drawContours(show, [box], -1, (150, 245, 245), 1)
        cv2.putText(show, "Ball", (x, y - 5), font, 0.7, (150, 245, 245), 1)
    if mask_color == 'b':
        mask_frame = ball_mask


class WebcamVideoStream:
    stream = None

    def __init__(self, src=0):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()

        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 1600)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 900)
        self.stream.set(cv2.CAP_PROP_BUFFERSIZE, 3)
        self.stream.set(cv2.CAP_PROP_EXPOSURE, 77)
        self.stream.set(cv2.CAP_PROP_BRIGHTNESS, 154)
        self.stream.set(cv2.CAP_PROP_GAIN, 106)
        self.stream.set(cv2.CAP_PROP_FOCUS, 0)

    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=(), name='camera_thread').start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if exit_bit == 1:
                return

            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True


def image_func():
    global frame_counter, ball_pos_last, show, frame, ball_speed, point_show, current_window, mask, ball_dir, cap
    cap = WebcamVideoStream(src=camera_num).start()
    tStart = 0
    while True:
        if frame_counter == 0:
            tStart = time.time()
        frame_counter += 1
        ret, frame = (1, cap.read())

        if not ret:
            break
        if len(frame) == 0:
            continue
        show = frame.copy()

        # thread begin
        thread2 = Thread(target=thread_our, name='T2', daemon=True)
        thread3 = Thread(target=thread_enemy, name='T3', daemon=True)
        thread4 = Thread(target=thread_color1, name='T4', daemon=True)
        thread5 = Thread(target=thread_color2, name='T5', daemon=True)
        thread6 = Thread(target=thread_color3, name='T6', daemon=True)
        thread7 = Thread(target=thread_ball, name='T7', daemon=True)
        thread2.start()
        thread3.start()
        thread4.start()
        thread5.start()
        thread6.start()
        thread7.start()

        cv2.waitKey(1)

        thread2.join()
        thread4.join()

        for our in our_pos:
            for color1 in color1_pos:
                if get_distance(our, color1) < 30:
                    cv2.line(show, our, color1, (255, 255, 255), 1)
                    cv2.putText(show, "ROBOT_1", our, font, 0.6, (255, 255, 255), 1)
                    cv2.circle(show, our, 2, (252, 255, 255), -1)
                    dist = get_distance(our, color1)
                    try:
                        our_dir[0] = [(our[0] - color1[0]) / dist, (our[1] - color1[1]) / dist]
                    except ZeroDivisionError:
                        our_dir[0] = [0, 0]
                    if error_open:
                        q = error_correct(our)
                        cv2.circle(show, (q[0], q[1]), 3, (252, 255, 255), -1)
                        our_data[0] = [q[0], q[1]]

        thread5.join()
        for our in our_pos:
            for color2 in color2_pos:
                if get_distance(our, color2) < 30:
                    cv2.line(show, our, color2, (255, 255, 255), 1)
                    cv2.putText(show, "ROBOT_2", our, font, 0.6, (255, 255, 255), 1)
                    cv2.circle(show, our, 2, (252, 255, 255), -1)
                    dist = get_distance(our, color2)
                    try:
                        our_dir[1] = [(our[0] - color2[0]) / dist, (our[1] - color2[1]) / dist]
                    except ZeroDivisionError:
                        our_dir[1] = [0, 0]
                    if error_open:
                        q = error_correct(our)
                        cv2.circle(show, (q[0], q[1]), 3, (252, 255, 255), -1)
                        our_data[1] = [q[0], q[1]]

        thread6.join()
        for our in our_pos:
            for color3 in color3_pos:
                if get_distance(our, color3) < 30:
                    cv2.line(show, our, color3, (255, 255, 255), 1)
                    cv2.putText(show, "ROBOT_3", our, font, 0.6, (255, 255, 255), 1)
                    cv2.circle(show, our, 2, (252, 255, 255), -1)
                    dist = get_distance(our, color3)
                    try:
                        our_dir[2] = [(our[0] - color3[0]) / dist, (our[1] - color3[1]) / dist]
                    except ZeroDivisionError:
                        our_dir[2] = [0, 0]
                    if error_open:
                        q = error_correct(our)
                        cv2.circle(show, (q[0], q[1]), 3, (252, 255, 255), -1)
                        our_data[2] = [q[0], q[1]]

        # print(our_data)

        thread3.join()
        enemy_code = 0
        global enemy_data
        enemy_data = [[], [], []]
        for enemy in enemy_pos:
            enemy_code += 1
            if enemy_code > 3:
                break
            elif error_open:
                q = error_correct(enemy)
                cv2.circle(show, (q[0], q[1]), 3, (252, 255, 255), -1)
                cv2.putText(show, "ENEMY", (q[0], q[1]), font, 0.6, (255, 255, 255), 1)
                enemy_data[enemy_code - 1] = [q[0], q[1]]
            else:
                cv2.putText(show, "ENEMY", enemy, font, 0.6, (255, 255, 255), 1)
                cv2.circle(show, enemy, 2, (252, 255, 255), -1)

        #  印出場地的點線
        if point_show:
            if len(field_pos) > 0:
                temp_x = 0.0
                temp_y = 0.0
                field_pos_switch = False
                first_x = field_pos[0][0]
                first_y = field_pos[0][1]
                for i in field_pos:
                    x = i[0]
                    y = i[1]
                    if field_pos_switch:
                        cv2.line(frame, (temp_x, temp_y), (x, y), 255, 3)
                    temp_x = i[0]
                    temp_y = i[1]
                    cv2.circle(frame, (x, y), 5, 255, -3)
                    field_pos_switch = True
                if len(field_pos) == 12:
                    cv2.line(frame, (first_x, first_y), (x, y), 255, 3)
            for i in penalty_pos:
                x = i[0]
                y = i[1]
                cv2.circle(frame, (x, y), 5, (2, 34, 59), -3)
            for i in FK_pos:
                x = i[0]
                y = i[1]
                cv2.circle(frame, (x, y), 5, (255, 34, 59), -3)
            for i in PK_pos:
                x = i[0]
                y = i[1]
                cv2.circle(frame, (x, y), 5, (155, 255, 255), -3)
            for i in FB_pos:
                x = i[0]
                y = i[1]
                cv2.circle(frame, (x, y), 5, (45, 155, 150), -3)
            cv2.circle(frame, (middle[0], middle[1]), 5, (255, 255, 250), -3)
            cv2.putText(show, "MIDDLE", (middle[0], middle[1]), font, 0.6, (255, 255, 255), 1)
            cv2.circle(frame, (camera_project[0], camera_project[1]), 5, (255, 255, 250), -3)
            cv2.putText(show, "CAMERA_PROJECTION", (camera_project[0], camera_project[1]), font, 0.6, (255, 255, 255),
                        1)

        our_pos.clear()
        enemy_pos.clear()
        color1_pos.clear()
        color2_pos.clear()
        color3_pos.clear()

        #  command order

        #  from strategy show
        Str = str(int(ball_speed))
        cv2.putText(show, Str, (ball_pos_now[0], ball_pos_now[1] - 30), font, 1, (150, 245, 245), 3)

        if (challenge_bit == 3) & (len(ch3.robots) == 3):

            for i in range(3):
                if ch3.robots[i].job == ch3.Job.SHOOT:
                    cv2.putText(show, "SHOOT", (our_data[i][0], our_data[i][1] - 20), font, 1, (84, 83, 268), 3)
                if ch3.robots[i].job == ch3.Job.DIVE:
                    cv2.putText(show, "DIVE", (our_data[i][0], our_data[i][1] - 20), font, 1, (84, 83, 268), 3)
                if ch3.robots[i].job == ch3.Job.PASS:
                    cv2.putText(show, "PASS", (our_data[i][0], our_data[i][1] - 20), font, 1, (84, 83, 268), 3)

            if not ch3.robots[0].next[0] == 0:
                cv2.circle(show, (int(ch3.robots[0].next[0]), int(ch3.robots[0].next[1])), 5, (45, 165, 230), -3)
                cv2.line(show, (our_data[0][0], our_data[0][1]),
                         (int(ch3.robots[0].next[0]), int(ch3.robots[0].next[1])), (45, 165, 230), 3)
                cv2.putText(show, "ROBO1_NEXT", (int(ch3.robots[0].next[0]), int(ch3.robots[0].next[1])), font, 0.6,
                            (45, 165, 230), 1)
            if not ch3.robots[1].next[0] == 0:
                cv2.circle(show, (int(ch3.robots[1].next[0]), int(ch3.robots[1].next[1])), 5, (150, 205, 0), -3)
                cv2.line(show, (our_data[1][0], our_data[1][1]),
                         (int(ch3.robots[1].next[0]), int(ch3.robots[1].next[1])), (150, 205, 0), 3)
                cv2.putText(show, "ROBO2_NEXT", (int(ch3.robots[1].next[0]), int(ch3.robots[1].next[1])), font, 0.6,
                            (150, 205, 0), 1)
            if not ch3.robots[2].next[0] == 0:
                cv2.circle(show, (int(ch3.robots[2].next[0]), int(ch3.robots[2].next[1])), 5, (220, 50, 200), -3)
                cv2.line(show, (our_data[2][0], our_data[2][1]),
                         (int(ch3.robots[2].next[0]), int(ch3.robots[2].next[1])), (220, 50, 200), 3)
                cv2.putText(show, "ROBO3_NEXT", (int(ch3.robots[2].next[0]), int(ch3.robots[2].next[1])), font, 0.6,
                            (220, 50, 200), 1)
        elif challenge_bit == 2 and len(ch2.robots) == 1:
            for i, robo in enumerate(ch2.robots):
                if our_data[i]:
                    if robo.job == ch2.Job.SHOOT:
                        cv2.putText(show, "SHOOT", (our_data[i][0], our_data[i][1] - 20), font, 1, (84, 83, 268), 3)
                        if not robo.target[0] == -1:
                            cv2.circle(show, (int(robo.target[0]), int(robo.target[1])), 5, (45, 165, 230), -3)
                    if robo.job == ch2.Job.NONE:
                        cv2.putText(show, "NONE", (our_data[i][0], our_data[i][1] - 20), font, 1, (84, 83, 268), 3)
                    if robo.job == ch2.Job.PASS:
                        cv2.putText(show, "PASS", (our_data[i][0], our_data[i][1] - 20), font, 1, (84, 83, 268), 3)

            if not ch2.robots[0].next[0] == -1:
                cv2.circle(show, (int(robo.next[0]), int(robo.next[1])), 5, (45, 165, 230), -3)
                cv2.line(show, (our_data[0][0], our_data[0][1]),
                         (int(robo.next[0]), int(robo.next[1])), (45, 165, 230), 3)
                cv2.putText(show, "ROBO1_NEXT", (int(robo.next[0]), int(robo.next[1])), font, 0.6,
                            (45, 165, 230), 1)
            if not ch2.ball.kick == -1:
                cv2.circle(show, (int(ch2.ball.kick[0]), int(ch2.ball.kick[1])), 5, (45, 165, 230), -3)
        elif challenge_bit == 1 and len(ch1.robots) == 2:
            for i, robo in enumerate(ch1.robots):
                if our_data[i]:
                    if robo.job == ch1.Job.SHOOT:
                        cv2.putText(show, "SHOOT", (our_data[i][0], our_data[i][1] - 20), font, 0.8, (84, 83, 268), 3)
                        if not robo.target[0] == -1:
                            cv2.circle(show, (int(robo.target[0]), int(robo.target[1])), 5, (45, 165, 230), -3)
                    if robo.job == ch1.Job.NONE:
                        cv2.putText(show, "NONE", (our_data[i][0], our_data[i][1] - 20), font, 0.8, (84, 83, 268), 3)
                    if robo.job == ch1.Job.LEAVE:
                        cv2.putText(show, "LEAVE", (our_data[i][0], our_data[i][1] - 20), font, 0.8, (84, 83, 268), 3)
                    if robo.job == ch1.Job.REST:
                        cv2.putText(show, "REST", (our_data[i][0], our_data[i][1] - 20), font, 0.8, (84, 83, 268), 3)
                    if robo.job == ch1.Job.PASS:
                        cv2.putText(show, "PASS", (our_data[i][0], our_data[i][1] - 20), font, 0.8, (84, 83, 268), 3)
                        if not robo.target[0] == -1:
                            cv2.circle(show, (int(robo.target[0]), int(robo.target[1])), 5, (45, 165, 230), -3)
                    
            if not ch1.robots[0].next[0] == -1:
                robo = ch1.robots[0]
                cv2.circle(show, (int(robo.next[0]), int(robo.next[1])), 5, (45, 165, 230), -3)
                cv2.line(show, (our_data[0][0], our_data[0][1]),
                         (int(robo.next[0]), int(robo.next[1])), (45, 165, 230), 3)
                cv2.putText(show, "ROBO1_NEXT", (int(robo.next[0]), int(robo.next[1])), font, 0.6,
                            (45, 165, 230), 1)
            if not ch1.robots[1].next[0] == -1:
                robo = ch1.robots[1]
                cv2.circle(show, (int(robo.next[0]), int(robo.next[1])), 5, (150, 205, 0), -3)
                cv2.line(show, (our_data[1][0], our_data[1][1]),
                         (int(robo.next[0]), int(robo.next[1])), (150, 205, 0), 3)
                cv2.putText(show, "ROBO2_NEXT", (int(robo.next[0]), int(robo.next[1])), font, 0.6,
                            (150, 205, 0), 1)
        #  print("cost %f second" % (tEnd - tStart))  # 紀錄每一幀時間
        thread7.join()

        # 顯示畫面
        if mask & once_open_mask:
            cv2.imshow(current_window, mask_frame)
        cv2.imshow("camera_RGB", frame)  # 原本相機
        cv2.imshow("camera", show)  # 有標註顏色過後的

        if exit_bit == 1:
            cv2.destroyAllWindows()
            break

        if frame_counter >= 10:
            move_distance = get_distance(ball_pos_last, ball_pos_now)
            if move_distance == 0:
                x = 0
                y = 0
            else:
                x = (ball_pos_now[0] - ball_pos_last[0]) / move_distance
                y = (ball_pos_now[1] - ball_pos_last[1]) / move_distance

            ball_dir = [x, y]
            ball_pos_last = ball_pos_now
            tEnd = time.time()
            time_interval = tEnd - tStart
            try:
                ball_speed = move_distance / time_interval
            except ZeroDivisionError:
                ball_speed = 0
                print("speed error")
            # print("ball speed:", ball_speed, ", ball speed vector:", ball_speed_vector, ", time:", time_interval)
            frame_counter = 0


if __name__ == '__main__':
    image_func()
