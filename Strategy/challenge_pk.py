"""
In this vision , robot can only do things below
1.robot won't easily change ist position (upper side or downward side)
2.
"""

# import constant
from enum import Enum
import numpy as np
import math
import cv2
from Strategy import constant as CONST
import time

PRINT = False

ID_IN_USE = 3
CM_TO_PIX = 3.0
SIDE = -1  # -1 for <- , 1 for ->

BOUNDARY = []
CENTER = [0, 0]
PENALTY = [[], [], [], []]

our_gate = []  # gate_left to gate_right , penalty_left to penalty_right
enemy_gate = []

# CONST
WAY_ANGLE = {'FORE': 0, 'LEFT': -math.pi / 2, 'RIGHT': math.pi / 2, 'BACK': math.pi}

ball = None
robots = [[], [], []]


def strategy_update_field(side, boundary, center, penalty):
    global SIDE, BOUNDARY, CENTER, PENALTY, x_length, y_length, our_gate, enemy_gate
    SIDE = side
    BOUNDARY = boundary
    CENTER = center
    PENALTY = penalty
    #  set gate
    if SIDE == 1:  # ->
        our_gate = [BOUNDARY[11], BOUNDARY[8], PENALTY[0], PENALTY[3]]
        enemy_gate = [BOUNDARY[5], BOUNDARY[2], PENALTY[2], PENALTY[1]]
    else:
        our_gate = [boundary[5], BOUNDARY[2], PENALTY[2], PENALTY[1]]
        enemy_gate = [boundary[11], BOUNDARY[8], PENALTY[0], PENALTY[3]]
    print("SIDE", SIDE)
    print("BOUNDARY", BOUNDARY)
    print("CENTER", CENTER)
    print("PENALTY", PENALTY)


def Initialize():
    global robots, ball
    robots.append(Robot(ID_IN_USE))
    ball = Ball()


def Update_Robo_Info(teamD, teamP, oppoP, ballP, ballS, ballD):
    global robots
    close_ball = [-1, 1000]  # first element is enemy index , second is distance to the ball
    for i in range(3):
        robots[i].miss = False
        if not teamP[i]:
            robots[i].miss = True
        else:
            # robots[i].pos = [simulator_adjust(teamP[i], False)[0], simulator_adjust(teamP[i], False)[1]]

            robots[i].pos = teamP[i]
            robots[i].dir = teamD[i]
            robots[i].distance = get_distance(robots[i].pos, ball.pos)
        robots[i].target = [0, 0]

    # ball.pos = simulator_adjust(ballP, False)
    ball.pos = ballP
    ball.speed = ballS
    ball.dir = ballD


def strategy():
    global ball, robots
    assign_role()

    #    print(
    #       "[ID{id}][pos{pos}][dir{dir}][role {role}][half {half}][job {job}]".format(id=robots[0].ID,
    #                                                                                 pos=robots[0].pos,
    #                                                                                dir=robots[0].dir,
    #                                                                               role=robots[0].role,
    #                                                                              half=robots[0].half,
    #                                                                             job=robots[0].job))

    cmd = ['N', 'N', 'N']
    try:
        cmd[2] = execute_job(0)
    except ZeroDivisionError:
        print('divide zero...')
        cmd[2] = 'N'
    except Exception as e:
        print('Catch Error.....')
        print(e)
        cmd[2] = 'N'
    if PRINT:
        print(cmd)
        print()
    return cmd


def assign_role():
    """
    Decide every robot's role and change robot's attribute: role
    """
    global ball, robots
    if not robots[2].miss:
        robots[2].role = Role.KEEPER
        robots[2].keeper_assign()
    if not robots[0].miss:
        robots[0].role = Role.STRIKER
        robots[0].striker_assign()
    else:
        if PRINT:
            print("keeper miss")


def execute_job(id):
    global robots
    robo = robots[id]
    # if robo.job == Job.STAND:
    #    # face ball
    #    arrival = robo.pos
    #    ideal_dir = [b - r for b, r in zip(ball.pos, robo.pos)]
    #    change, rt_cmd = move_with_dir(robo, arrival, robo.dir, ideal_dir, fit_way='FORE', ways=[])
    #    if change:
    #        return rt_cmd
    #    else:
    #        return 'R'
    if robo.job == Job.DIVE:
        x_dist = our_gate[0][0] - ball.pos[0]
        if x_dist * ball.dir[0] > 0:
            y_des = ball.pos[1] + x_dist / ball.dir[0] * ball.dir[1]
            if our_gate[1][1] < y_des < our_gate[0][1] or our_gate[0][1] < y_des < our_gate[1][1]:
                if abs(robo.pos[1] - y_des) > robo.BODY['width'] * CM_TO_PIX / 2:
                    if (robo.pos[1] - y_des) * SIDE > 0:
                        return robo.MOTION['DEFENCE']['LEFT']['CMD'][0]
                    else:
                        return robo.MOTION['DEFENCE']['RIGHT']['CMD'][0]
    elif robo.job == Job.REST:
        return robo.MOTION['REST']['CMD'][0]
    return 'N'


def get_distance(start, end):
    try:
        distance = math.pow((start[0] - end[0]), 2) + math.pow((start[1] - end[1]), 2)
        distance = int(math.sqrt(distance))
    except IndexError:
        distance = 0
    return distance


def unit_vector(start, end):
    dist = get_distance(start, end)
    x = (end[0] - start[0]) / dist
    y = (end[1] - start[1]) / dist
    return [x, y]


def _dist(pos1, pos2):
    """return absolute distance between [x1,y1], [x2,y2]"""
    return math.hypot(pos1[0] - pos2[0], pos1[1] - pos2[1])


def _unit_vector(start, end):
    """return unit vector from start to end"""
    vector = [e - s for s, e in zip(start, end)]
    length = math.hypot(vector[0], vector[1])
    if length == 0:
        uniVector = [0, 0]
    else:
        uniVector = [comp / length for comp in vector]
    return uniVector


def _dot(x, y):
    """
       Dot product as sum of list comprehension doing element-wise multiplication
    """
    return sum(x_i * y_i for x_i, y_i in zip(x, y))


def _angle(a, b):
    """
       return angle from dir a to dir b, +(counterclocwise), from -180 to 180
    """
    for vec in [a, b]:
        length = math.hypot(vec[0], vec[1])
        try:
            vec[0] = vec[0] / length
            vec[1] = vec[1] / length
        except ZeroDivisionError:
            vec[0] = 0
            vec[1] = 0
    cross = a[0] * b[1] - a[1] * b[0]
    angle = math.asin(cross)
    dot = _dot(a, b)
    if dot < 0:
        if angle > 0:
            angle = math.acos(dot)
        else:
            angle = -math.acos(dot)
    return angle


def _rotate(vector, angle):
    """
       rotate vector by angle(radius) in counterclockwise direction
    """
    rot_vector = [0.0, 0.0]
    rot_vector[0] = (math.cos(angle) * vector[0]) - (math.sin(angle) * vector[1])
    rot_vector[1] = (math.sin(angle) * vector[0]) + (math.cos(angle) * vector[1])
    return rot_vector


def takeY(e):
    return e[1]


class Robot:
    """
    Attributes:
        ID: An int stands for the robot's ID(1-7)
        pos: An list[x,y] stands for the robot's position
        dir: list[x,y] -> The direction the robot faces, stored in unit vector
        role: A Role(Enum) represents the robot's role
        job: A Job(Enum) -> the move the robots are going to execute
        MOTION: motion constants from constant.py
        BODY: robot size from constant.py
    """

    def __init__(self, ID):
        self.ID = ID
        self.pos = [0, 0]  # position now
        self.dir = [0, 0]  # direction now face to
        self.role = Role.KEEPER
        self.half = 'middle_side'  # record in upper half or downward half field
        self.job = Job.NONE
        self.distance = 1000
        self.next = [0, 0]  # next place to go
        self.target = [0, 0]  # where to pass ball
        self.howclose = CONST.TREATING_ZONE * CM_TO_PIX  # minimum distance to judge shooting
        self.face_ball = False  # 注意防守時候須不需要面向敵人
        self.MOTION = CONST.getMotion(ID)
        self.BODY = CONST.getBody()
        self.miss = False

    def keeper_assign(self):
        # 戰略：1判斷球的速度，如果是在危險區域之內判斷方向後直接撲球
        #      2中央區站位為正中間
        #      3左邊/右邊的站位都是底線＋球門正中心連線
        #      4球的速度降低後便會出來踢球（如果是最近的）
        #      5沒事多休息
        global ball

        if (ball.pos[0] - our_gate[0][0] - 50 * CM_TO_PIX * SIDE) * SIDE < 0:
            self.job = Job.DIVE
        else:
            self.job = Job.REST
        print(self.job)


class Job(Enum):
    STAND = 0  # 站定位
    SHOOT = 5  # 射門
    DIVE = 8  # 撲球
    REST = 9  # 蹲下
    NONE = 10


class Role(Enum):
    KEEPER = 1  # 守門


class Ball:
    def __init__(self):
        self.pos = [0, 0]
        self.speed = 0  # speed rank
        self.dir = [0, 0]
        self.status = 'free'
        self.radius = CONST.BALL_RADIUS
