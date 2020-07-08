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

# Parameter needed to adjust
ID_IN_USE = [4, 4, 6]
CM_TO_PIX = 3.0
carrier_range = 18 * CM_TO_PIX  # range to judge if carry ball
line_range = 7 * CM_TO_PIX  # when defend , we need to know how close is enough from defend line
SIDE = -1  # -1 for <- , 1 for ->
ROB_RANG = 35  # enemy's half width

# global value of movable objects
robots = []
enemies = []
ball = None
assist_block = False  # 只有到達當前位置的時候才會執行下一個目標點

# Field Parameter
BOUNDARY = []
CENTER = [0, 0]
PENALTY = [[], [], [], []]

our_gate = []  # gate_left to gate_right , penalty_left to penalty_right
enemy_gate = []

# Define of zone
x_length = 340 * CM_TO_PIX / 2
y_length = 180 * CM_TO_PIX / 2

# CONST
WAY_ANGLE = {'FORE': 0, 'LEFT': -math.pi / 2, 'RIGHT': math.pi / 2, 'BACK': math.pi}

robot1_buffer = [[], [], [], [], []]
robot2_buffer = [[], [], [], [], []]
robot3_buffer = [[], [], [], [], []]
last_point = [[], [], []]
mistake_counter = 0


def simulator_adjust(pos, reverse):
    if reverse:
        x = int((pos[0] - 160) / 1200 * 730 + 140)
        y = int((pos[1] - 100) / 636 * 380 + 70)
    else:
        x = int(160 + 1200 * ((pos[0] - 140) / 730))
        y = int(100 + 636 * ((pos[1] - 70) / 380))
    return x, y


def strategy_update_field(side, boundary, center, penalty):
    """
    Description:
        Pass field information into strategy system.
        This will be called only once by the simulator.
    Parameter:
        param1: 0/1 -> 1 if left attack right, -1 if right attack left
        param2: list[list(int)] -> 12 boundary points of the field
        param3: list[int] -> center of the field
        param4: list[list(int)] -> 4 penalty corner
    """
    # Your code

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
    if PRINT:
        pass
        # print(SIDE)
        # print(BOUNDARY)
        # print(CENTER)
        # print(PENALTY)
        # print(FB_x)
        # print(FB_y)
        # print(GA_x)
        # print(GA_y)
    print("oooooooooooo")
    print(SIDE)
    print(BOUNDARY)
    print(CENTER)
    print(PENALTY)


def Initialize():
    """
    Description:
        Initialise the strategy.
        This function will be called by the simulator before a simulation is started.
    """
    global robots, enemies, ball
    for i in range(3):
        robots.append(Robot(ID_IN_USE[i]))
    for i in range(3):
        enemies.append(Enemy())
    ball = Ball()


def draw_on_simulator(frame):
    """
    Description:
        Draw whatever you want on the simulator.
        Before the simulator update window, it will call this function and you can just draw anything you want.
        This function will be called every time the simulator is going to update frame.
        This function will be called everytime the simulator is going to update frame.
    Parameter:
        param1: numpy array -> the frame that will be displayed
    Return:
        retva1: numpy array -> the frame that will be displayed
    """
    # Your code
    global robots, ball
    cv2.circle(frame, simulator_adjust(robots[0].next, True), 5, (0, 102, 204), -1, 8, 0)
    cv2.putText(frame, "robot1", simulator_adjust(robots[0].next, True), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 102, 204),
                1)
    cv2.circle(frame, simulator_adjust(robots[1].next, True), 5, (0, 204, 204), -1, 8, 0)
    cv2.putText(frame, "robot2", simulator_adjust(robots[1].next, True), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 204, 204),
                1)
    cv2.circle(frame, simulator_adjust(robots[2].next, True), 5, (0, 204, 0), -1, 8, 0)
    cv2.putText(frame, "robot3", simulator_adjust(robots[2].next, True), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 204, 0),
                1)
    cv2.circle(frame, simulator_adjust(enemy_gate[0], True), 5, (0, 150, 0), -1, 8, 0)
    cv2.circle(frame, simulator_adjust(enemy_gate[1], True), 5, (0, 150, 0), -1, 8, 0)

    for i in range(3):
        if robots[i].job == Job.SHOOT:
            cv2.putText(frame, "SHOOT", simulator_adjust(robots[i].pos, True), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (255, 255, 255), 1)
        if robots[i].job == Job.PASS:
            cv2.putText(frame, "PASS", simulator_adjust(robots[i].pos, True), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (255, 255, 255), 1)
        if robots[i].target[0] == -1 & robots[i].target[1] == -1:
            pass
        elif robots[i].target[0] == 0 & robots[i].target[1] == 0:
            pass
        else:
            cv2.circle(frame, simulator_adjust(robots[i].target, True), 5, (255, 250, 0), -1, 8, 0)
            cv2.putText(frame, "target", simulator_adjust(robots[i].target, True), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (255, 255, 0), 1)
            cv2.line(frame, simulator_adjust(ball.pos, True), simulator_adjust(robots[i].target, True), (255, 255, 0),
                     1)
    return frame


def Update_Robo_Info(teamD, teamP, oppoP, ballP, ballS, ballD):
    """
    Description:
        Pass robot and ball info into strategy.
        This function will be called before every time the simulator ask for strategy
    Parameter:
        param1: list[list[float]] -> [x,y] for our teammate robot direction
        param2: list[list[int]] -> [x,y] for our teammate robot position
        This function will be called before everytime the simulator ask for strategy
    Parameter:
        param1: list[list[float]] -> [x,y] for our teammate robot direction
        param2: list[list[int]] -> [x,y] for our teammate robot position
        param3: list[list[int]] -> [x,y] for opponent's robot position
        param4: list[int] -> [x,y] for ball position
    """
    global robots, enemies
    close_ball = [-1, 1000]  # first element is enemy index , second is distance to the ball
    for i in range(3):
        robots[i].miss = False
        enemies[i].miss = False
        if not teamP[i]:
            robots[i].miss = True
        else:
            # robots[i].pos = [simulator_adjust(teamP[i], False)[0], simulator_adjust(teamP[i], False)[1]]

            robots[i].pos = teamP[i]
            robots[i].dir = teamD[i]
            robots[i].distance = get_distance(robots[i].pos, ball.pos)
            robots[i].in_zone = in_zone(robots[i].pos)
        robots[i].target = [0, 0]
        if not oppoP[i]:
            enemies[i].miss = True
        else:
            enemies[i].carrier = False
            # enemies[i].pos = [simulator_adjust(oppoP[i], False)[0], simulator_adjust(oppoP[i], False)[1]]
            enemies[i].pos = oppoP[i]
            enemies[i].distance = get_distance(enemies[i].pos, ball.pos)
            if (enemies[i].distance < close_ball[1]) & (enemies[i].distance < carrier_range):
                close_ball = [i, enemies[i].distance]  # who is most likely carrier ball
            #  and check in witch zone
            enemies[i].in_zone = in_zone(enemies[i].pos)

    if close_ball[0] != -1:
        enemies[close_ball[0]].carrier = True

    # ball.pos = simulator_adjust(ballP, False)
    ball.pos = ballP
    ball.speed = ballS

    ball.dir = ballD
    ball.in_zone = in_zone(ball.pos)
    #    print("ball_inZone:", ball.in_zone)
    if PRINT:
        print("ball_inZone:", ball.in_zone)
        # print(teamD, teamP, oppoP, ball.pos, ball.speed, ball.dir)
        """print("ball_inzone")
        print(ball.pos)
        print(ball.in_zone)"""
        # return False


def strategy():
    """
    Description:
        The simulator will ask for strategy after calling Update_Robo_Info()
    Return:
        retva1: str -> command for this robot
    """
    global ball, robots, enemies

    mode = set_mode()
    # as a defender or an attacker

    assign_role(mode)

    for i in range(3):
        robots[i].next = [int(robots[i].next[0]), int(robots[i].next[1])]
        robots[i].target = [int(robots[i].target[0]), int(robots[i].target[1])]

    robot1_buffer[mistake_counter % 5] = robots[0].next
    noise = False
    for vib in robot1_buffer:
        if not vib:
            continue
        else:
            if get_distance(vib, robots[0].next) > 5 * CM_TO_PIX:
                noise = True
                break
    if noise:
        robots[0].next = last_point[0]
    else:
        last_point[0] = robots[0].next

    robot2_buffer[mistake_counter % 5] = robots[1].next
    noise = False
    for vib in robot2_buffer:
        if not vib:
            continue
        else:
            if get_distance(vib, robots[1].next) > 5 * CM_TO_PIX:
                noise = True
                break
    if noise:
        robots[1].next = last_point[1]
    else:
        last_point[1] = robots[1].next

    robot3_buffer[mistake_counter % 5] = robots[2].next
    noise = False
    for vib in robot3_buffer:
        if not vib:
            continue
        else:
            if get_distance(vib, robots[2].next) > 5 * CM_TO_PIX:
                noise = True
                break
    if noise:
        robots[2].next = last_point[2]
    else:
        last_point[2] = robots[2].next

    if PRINT:

        for i in range(3):
            print("[ID{id}][dist{dist}][carry{carry}]".format(id=i, dist=enemies[i].distance, carry=enemies[i].carrier))

            print(
                "[ID{id}][pos{pos}][dir{dir}][role {role}][half {half}][job {job}]".format(id=robots[i].ID,
                                                                                           pos=robots[i].pos,
                                                                                           dir=robots[i].dir,
                                                                                           role=robots[i].role,
                                                                                           half=robots[i].half,
                                                                                           job=robots[i].job))
            print(
                "[dis{dis}][miss{miss}][next{next}][tar{tar}][zon {zon}][close{clo}][face {fac}]".format(
                    dis=robots[i].distance,
                    miss=robots[i].miss,
                    next=robots[i].next,
                    tar=robots[i].target,
                    zon=robots[i].in_zone,
                    clo=robots[i].howclose,
                    fac=robots[i].face_ball))
            print("\n")
    cmd = ['N', 'N', 'N']
    for i in range(len(robots)):
        try:
            cmd[i] = execute_job(i)
        except ZeroDivisionError:
            print('divide zero...')
            cmd[i] = 'N'
        except Exception as e:
            print('Catch Error.....')
            print(e)
            cmd[i] = 'N'
    if PRINT:
        print(cmd)
        print()
    return cmd


def get_sent_cmd(sentcmd, update):
    """
    Description:
        Simulator will pass the received strategy and a sending state
    Parameter:
        param1: list[str] -> received command
        param2: bool -> sent or not
    """
    # Your code
    pass


def set_mode():
    global ball, SIDE
    return Mode.OFFENSE if (ball.pos[0] - CENTER[0]) * SIDE > 0 else Mode.DEFENSE


def half_field():
    global robots
    if (robots[0].pos[1] - robots[1].pos[1]) * SIDE > 0:
        robots[0].half = 'right_side'
        robots[1].half = 'left_side'
    else:
        robots[1].half = 'right_side'
        robots[0].half = 'left_side'


def assign_role(mode):
    """
    Decide every robot's role and change robot's attribute: role
    """
    global ball, robots

    if not robots[2].miss:
        distance_keeper = get_distance(robots[2].pos, ball.pos)
        robots[2].role = Role.KEEPER
        robots[2].keeper_assign(mode)

    half_field()
    for i in range(2):
        if not robots[i].miss:
            if mode == Mode.OFFENSE:
                robots[i].role = Role.STRICKER
                robots[i].stricker_assign(abs(i - 1))
            elif mode == Mode.DEFENSE:
                robots[i].role = Role.COUNTER
                robots[i].counter_assign()

    if (not robots[0].miss) & (not robots[1].miss):
        distance_1 = get_distance(robots[0].pos, ball.pos)
        distance_2 = get_distance(robots[1].pos, ball.pos)

        if mode == Mode.OFFENSE:
            if distance_1 < distance_2:
                robots[0].role = Role.STRICKER
                robots[0].stricker_assign(1)
                robots[1].role = Role.ASSISTER
                robots[1].assister_assign(0)
            else:
                robots[1].role = Role.STRICKER
                robots[1].stricker_assign(0)
                robots[0].role = Role.ASSISTER
                robots[0].assister_assign(1)
        elif mode == Mode.DEFENSE:
            if distance_1 < distance_2:
                robots[0].role = Role.COUNTER
                robots[0].counter_assign()
                robots[1].role = Role.INTERFERER
                robots[1].interferer_assign(0)
            else:
                robots[1].role = Role.COUNTER
                robots[1].counter_assign()
                robots[0].role = Role.INTERFERER
                robots[0].interferer_assign(1)
        else:
            print("assign role error")


def execute_job(id):
    """
    Base on the robot's job, give an exact command
    """
    global robots
    robo = robots[id]
    if robo.job == Job.MOVE:
        move_ways = ['FORE', 'LEFT', 'BACK', 'RIGHT']
        moveable, rt_cmd = move(robo, robo.next, move_ways)
        if moveable:
            return rt_cmd
    elif robo.job == Job.STAND:
        # face ball
        arrival = robo.pos
        ideal_dir = [b - r for b, r in zip(ball.pos, robo.pos)]
        change, rt_cmd = move_with_dir(robo, arrival, robo.dir, ideal_dir, fit_way='FORE', ways=[])
        if change:
            return rt_cmd
        else:
            return 'R'
    elif robo.job == Job.PASS:
        if PRINT:
            print('job == pass')
        if robo.target[0] == -1:
            if PRINT:
                print('no aim')
        # kick ball
        check_boundary_ball(robo)
        kickable_dist = 3 * CM_TO_PIX  # the distance between ball and the robot should be
        kickable_ang = 15 / 180 * math.pi  # acceptable angle error when kicking
        kick_ways = ['FORE', 'LEFT', 'BACK', 'RIGHT']  # restrict to FORE??
        move_ways = ['FORE', 'LEFT', 'BACK', 'RIGHT']
        try:
            kick_dir = _unit_vector(ball.pos, robo.target)
            force = 'small'
            kickable, kick_way, rt_cmd, arrival = is_kickable(robo, kickable_dist, kickable_ang, kick_dir, kick_ways,
                                                              force)
            robo.next = arrival
        except ZeroDivisionError:
            print("ball has arrived the target")
            kickable = False
        if kickable:
            robo.job = Job.NONE
            robo.role = Role.ROAMER
            robo.target = [-1, -1]
            return rt_cmd
        movable, rt_cmd = move_with_dir(robo, arrival, _rotate(robo.dir, WAY_ANGLE[kick_way]), kick_dir, kick_way)
        if movable:
            return rt_cmd
    elif robo.job == Job.SHOOT:
        if robo.target[0] == -1:
            if PRINT:
                print('no target')
        if robo.target[0] != -1:
            check_boundary_ball(robo)
            force = 'big'
            kickable_dist = 3 * CM_TO_PIX  # the distance between arrival and the robot should be
            kickable_ang = 15 / 180 * math.pi  # acceptable angle error when kicking
            kick_ways = ['FORE', 'LEFT', 'BACK', 'RIGHT']
            move_ways = ['FORE', 'LEFT', 'BACK', 'RIGHT']
            kick_dir = _unit_vector(ball.pos, robo.target)
            kickable, kick_way, rt_cmd, arrival = is_kickable(robo, kickable_dist, kickable_ang, kick_dir, kick_ways,
                                                              force)
            robo.next = arrival  #
            if kickable:
                robo.job = Job.NONE
                robo.target = [-1, -1]
                return rt_cmd
            movable, rt_cmd = move_with_dir(robo, arrival, _rotate(robo.dir, WAY_ANGLE[kick_way]), kick_dir, kick_way,
                                            move_ways)
            if movable:
                return rt_cmd
            else:
                print("踢個毛")
    elif robo.job == Job.ACCURATE_SHOOT:
        pass
    elif robo.job == Job.DIVE:
        if ball.speed > CONST.DANGER_SPEED:
            x_dist = our_gate[0][0] - ball.pos[0]
            if x_dist * ball.dir[0] > 0:
                y_des = ball.pos[1] + x_dist / ball.dir[0] * ball.dir[1]
                if our_gate[1][1] < y_des < our_gate[0][1] or our_gate[0][1] < y_des < our_gate[1][1]:
                    if abs(robo.pos[1] - y_des) > robo.BODY['width'] * CM_TO_PIX / 2:
                        block_dir = [our_gate[0][0] - robo.pos[0], y_des - robo.pos[1]]
                        for orient in ['RIGHT', 'LEFT']:
                            temp_dir = _rotate(robo.dir, WAY_ANGLE[orient])
                            if _dot(temp_dir, block_dir) >= 0:
                                return robo.MOTION['DEFENCE'][orient]['CMD'][0]
    elif robo.job == Job.REST:
        return robo.MOTION['REST']['CMD'][0]
    return 'N'


#  function for calculation position
def get_distance(start, end):
    try:
        distance = math.pow((start[0] - end[0]), 2) + math.pow((start[1] - end[1]), 2)
        distance = int(math.sqrt(distance))
    except IndexError:
        distance = 0
    return distance


def in_line(start, end, pos, projection):  # projection :if ask in line or return projection point
    if not projection:
        y = end[1] - start[1]
        x = start[0] - end[0]
        p = end[0] * start[1] - start[0] * end[1]
        dist = int(math.fabs(y * pos[0] + x * pos[1] + p)) / (math.pow(y * y + x * x, 0.5))
        return True if dist < line_range else False
    else:
        x = np.array(pos)
        u = np.array(start)
        v = np.array(end)
        n = v - u
        d = get_distance(start, end)
        n = np.array([n[0] / d, n[1] / d])
        P = u + n * np.dot(x - u, n)
        return [int(P[0]), int(P[1])]


def line_fraction(start, end, fraction):  # 用來找出線段中間的某個位置設定為到達點
    x = int(start[0] + (end[0] - start[0]) * fraction)
    y = int(start[1] + (end[1] - start[1]) * fraction)
    if PRINT:
        print(x, y)
    return [x, y]


def unit_vector(start, end):
    dist = get_distance(start, end)
    x = (end[0] - start[0]) / dist
    y = (end[1] - start[1]) / dist
    return [x, y]


def find_line_point(robot, gate):
    global ball
    vector_a = [(robot[0] - ball.pos[0]), (robot[1] - ball.pos[1])]
    vector_b = [(gate[0] - ball.pos[0]), (gate[1] - ball.pos[1])]
    length_b = get_distance(gate, ball.pos)
    length = _dot(vector_b, vector_a) / (length_b * length_b)
    return [ball.pos[0] + length * vector_b[0], ball.pos[1] + length * vector_b[1]]


def ratio(ra_x, ra_y):  # return point actually in graph
    global SIDE, BOUNDARY, CENTER, x_length, y_length
    return [CENTER[0] - x_length * ra_x, CENTER[1] - y_length * ra_y]


def in_zone(pos):
    global SIDE, PENALTY
    ra_x = pos[0]
    ra_y = pos[1]
    if ((ra_x - ratio(7 * SIDE / 17, 1)[0]) * SIDE > 0) & ((ra_x - ratio(-7 * SIDE / 17, 1)[0]) * SIDE < 0):  # center
        return Zone.CENTER_AREA
    elif (ra_y - ratio(1, 6 * SIDE / 9)[1]) * SIDE < 0:  # far left
        if (ra_x - ratio(7 * SIDE / 17, 1)[0]) * SIDE < 0:
            return Zone.FAR_LEFT_DEFEND
        elif (ra_x - ratio(-7 * SIDE / 17, 1)[0]) * SIDE > 0:
            return Zone.FAR_LEFT_OFFEND
    elif (ra_y - ratio(1, -6 * SIDE / 9)[1]) * SIDE > 0:  # far right
        if (ra_x - ratio(7 * SIDE / 17, 1)[0]) * SIDE < 0:
            return Zone.FAR_RIGHT_DEFEND
        elif (ra_x - ratio(-7 * SIDE / 17, 1)[0]) * SIDE > 0:
            return Zone.FAR_RIGHT_OFFEND
    elif (ra_y > PENALTY[0][1]) & (ra_y < PENALTY[3][1]) & (ra_x < PENALTY[0][0] + 45):
        return Zone.OUR_PENALTY if SIDE == 1 else Zone.ENEMY_PENALTY
    elif (ra_y > PENALTY[0][1]) & (ra_y < PENALTY[3][1]) & (ra_x > PENALTY[1][0] - 45):
        return Zone.ENEMY_PENALTY if SIDE == 1 else Zone.OUR_PENALTY
    elif (ra_y - ratio(1, 2 * SIDE / 9)[1]) * SIDE < 0:  # left
        if (ra_x - ratio(7 * SIDE / 17, 1)[0]) * SIDE < 0:
            return Zone.LEFT_DEFEND
        elif (ra_x - ratio(-7 * SIDE / 17, 1)[0]) * SIDE > 0:
            return Zone.LEFT_OFFEND
    elif (ra_y - ratio(1, -2 * SIDE / 9)[1]) * SIDE > 0:  # right
        if (ra_x - ratio(7 * SIDE / 17, 1)[0]) * SIDE < 0:
            return Zone.RIGHT_DEFEND
        elif (ra_x - ratio(-7 * SIDE / 17, 1)[0]) * SIDE > 0:
            return Zone.RIGHT_OFFEND
    elif (ra_x - ratio(7 * SIDE / 17, 4 / 9)[0]) * SIDE < 0:
        return Zone.MIDDLE_DEFEND
    elif (ra_x - ratio(-7 * SIDE / 17, 4 / 9)[0]) * SIDE > 0:
        return Zone.MIDDLE_OFFENCE


'''
   Collection of vector operation in this program
'''


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
    angle = 0
    for vec in [a, b]:
        length = math.hypot(vec[0], vec[1])
        try:
            vec[0] = vec[0] / length
            vec[1] = vec[1] / length
        except ZeroDivisionError:
            vec[0] = 0
            vec[1] = 0
    cross = a[0] * b[1] - a[1] * b[0]
    if -1 <= cross <= 1:
        pass
        angle = math.asin(cross)
        dot = _dot(a, b)
        if dot < 0:
            if angle > 0:
                angle = math.acos(dot)
            else:
                angle = -math.acos(dot)
    elif cross > 1:
        angle = math.pi / 2
    else:
        angle = -math.pi / 2
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


"""movement function"""


def is_kickable(robo, tol_dist, tol_angle, kick_dir, ways, force):
    # Find kick way(R,L,F,B)
    kick_way = find_way(robo, kick_dir, ways)
    if PRINT:
        print()
        print('====in kickable===')
        print('robo, kick_dir', robo.dir, kick_dir)
        print('kick way:', kick_way)
    arrival = [b - un_dir * ball.radius * CM_TO_PIX for b, un_dir in zip(ball.pos, kick_dir)]
    ver_offst = [direct * -robo.MOTION['MOVE'][kick_way]['OFFSET'][0] * CM_TO_PIX for direct in kick_dir]
    hor_offst = [0, 0]
    if kick_way == 'FORE' or kick_way == 'BACK':
        angle = _angle(robo.dir, [ball - pos for ball, pos in zip(ball.pos, robo.pos)])
        foot = 'RIGHT' if angle > 0 else 'LEFT'
        direction = _rotate(kick_dir, WAY_ANGLE[foot])
        offst = -robo.MOTION['MOVE'][kick_way]['OFFSET'][1] * CM_TO_PIX if kick_way == 'FORE' else \
            robo.MOTION['MOVE'][kick_way]['OFFSET'][1] * CM_TO_PIX
        hor_offst = [direct * offst for direct in direction]
        if PRINT:
            print('foot:', foot)
    arrival = [arr + hor + ver for arr, hor, ver in zip(arrival, hor_offst, ver_offst)]
    if PRINT:
        print('arr changed:', arrival)
        print('kick-dist:', _dist(arrival, robo.pos))
    if _dist(arrival, robo.pos) < tol_dist:  # can reach the ball
        direction = _rotate(robo.dir, WAY_ANGLE[kick_way])
        angle = _angle(kick_dir, direction)
        if PRINT:
            print('kick-angle:', angle)
        if abs(angle) < tol_angle:  # with right angle
            if PRINT:
                print('======kicked!!!!')
                time.sleep(3)
            # assign the right CMD according to the strength
            if kick_way == 'FORE':
                if force == 'big':
                    if foot == 'LEFT':
                        rt_cmd = robo.MOTION['KICK']['FSHOOT']['CMD'][0]
                    else:
                        rt_cmd = robo.MOTION['KICK']['FSHOOT']['CMD'][1]
                else:
                    if foot == 'LEFT':
                        rt_cmd = robo.MOTION['KICK']['PASS']['CMD'][0]
                    else:
                        rt_cmd = robo.MOTION['KICK']['PASS']['CMD'][1]
            elif kick_way == 'LEFT':
                rt_cmd = robo.MOTION['KICK']['SSHOOT']['CMD'][0]
            elif kick_way == 'RIGHT':
                rt_cmd = robo.MOTION['KICK']['SSHOOT']['CMD'][1]
            elif kick_way == 'BACK':
                if foot == 'LEFT':
                    rt_cmd = robo.MOTION['KICK']['BSHOOT']['CMD'][0]
                else:
                    rt_cmd = robo.MOTION['KICK']['BSHOOT']['CMD'][1]
            if PRINT:
                print('kicked cmd, arr', rt_cmd, arrival)
            return True, kick_way, rt_cmd, arrival
    return False, kick_way, 'N', arrival


def move_with_dir(robo, arrival, curr_dir, ideal_dir, fit_way='FORE', ways=['FORE', 'LEFT', 'BACK', 'RIGHT'],
                  accurate=True):
    tol_dist = 10 * CM_TO_PIX  # start fitting the right direction
    safe_ball = 15 * CM_TO_PIX
    dist = _dist(robo.pos, arrival)
    dist_ball = _dist(robo.pos, ball.pos)
    if PRINT:
        print()
        print('===m w/ dir ===')
        print('dist:', dist)
    if dist > tol_dist and dist_ball > safe_ball:
        check, rt_cmd = move(robo, arrival, ways)
        if check:
            return True, rt_cmd
    '''fix angle'''
    angle = _angle(ideal_dir, curr_dir)
    if PRINT:
        print('move/angle diff:', angle)
    if angle > 0:  # should turn left
        if angle >= robo.MOTION['TURN']['LEFT']['BOUND'][0]:
            rt_cmd = robo.MOTION['TURN']['LEFT']['CMD'][0]
            return True, rt_cmd
        elif angle >= robo.MOTION['TURN']['LEFT']['BOUND'][1]:
            rt_cmd = robo.MOTION['TURN']['LEFT']['CMD'][1]
            return True, rt_cmd
    else:
        if abs(angle) >= robo.MOTION['TURN']['RIGHT']['BOUND'][0] and accurate:
            rt_cmd = robo.MOTION['TURN']['RIGHT']['CMD'][0]
            return True, rt_cmd
        elif abs(angle) >= robo.MOTION['TURN']['RIGHT']['BOUND'][1] and accurate:
            rt_cmd = robo.MOTION['TURN']['RIGHT']['CMD'][1]
            return True, rt_cmd
    '''move slightly'''
    WAYS = ['FORE', 'RIGHT', 'BACK', 'LEFT']
    for i in [1, 2, 3, 0]:
        move_way = WAYS[(WAYS.index(fit_way) + i) % 4]
        temp_dir = _rotate(curr_dir, math.pi / 2 * i)
        diff_vec = [k - p for k, p in zip(arrival, robo.pos)]
        product = _dot(temp_dir, diff_vec)
        if product >= robo.MOTION['MOVE'][move_way]['BOUND'][0] * CM_TO_PIX:
            too_close = is_close_ball(robo.pos, temp_dir, robo.MOTION['MOVE'][move_way]['BOUND'][0] * CM_TO_PIX)
            if (not too_close) or move_way == 'BACK':
                rt_cmd = robo.MOTION['MOVE'][move_way]['CMD'][0]
                return True, rt_cmd
        if len(robo.MOTION['MOVE'][move_way]['BOUND']) > 1:
            if product >= robo.MOTION['MOVE'][move_way]['BOUND'][1] * CM_TO_PIX:
                rt_cmd = robo.MOTION['MOVE'][move_way]['CMD'][1]
                return True, rt_cmd
    return False, 'N'


def move(robo, arrival, ways=['', '', '', '']):
    '''
       To move to assigned point and facing whatever direction
    '''
    move_dir = _unit_vector(robo.pos, arrival)
    dist = _dist(robo.pos, arrival)
    if dist > 30 * CM_TO_PIX:
        ways = ['RIGHT', 'LEFT']
    move_way = find_way(robo, move_dir, ways)
    if PRINT:
        print()
        print('---->move w/o dir arr:', arrival)
        print('move dir', move_dir)
        print('move way', move_way)
        print('dist', dist)
    # if the robot will pass the ball while moving
    dist_ball = _dist(robo.pos, ball.pos)
    if dist > dist_ball:
        ball_dir = _unit_vector(robo.pos, ball.pos)
        angle = abs(_angle(move_dir, ball_dir))
        if move_way == 'FORE' or move_way == 'BACK':
            avoid_dist = robo.BODY['width'] * CM_TO_PIX
        else:
            avoid_dist = robo.BODY['length'] * CM_TO_PIX
        safe_angle = math.atan(avoid_dist / dist_ball)
        if angle < safe_angle:
            # change arrival
            safe_angle = math.atan(avoid_dist+5*CM_TO_PIX / dist_ball)
            if PRINT:
                print('safe angle:', safe_angle/math.pi*180)
                print('change arrival because of the ball!!!!')
            product = -1
            re_dir = [0, 0]
            for sign in [-1, 1]:
                temp_dir = _rotate(ball_dir, sign * safe_angle)
                temp_product = _dot(move_dir, temp_dir)
                if temp_product > product:
                    product = temp_product
                    mag = math.sqrt(dist_ball ** 2 + avoid_dist ** 2)
                    for i in [0, 1]:
                        re_dir[i] = temp_dir[i] * mag
                        arrival[i] = robo.pos[i] + re_dir[i]
            move_dir = _unit_vector(robo.pos, arrival)
            move_way = find_way(robo, move_dir, ways)
            dist = _dist(robo.pos, arrival)
    # fix angle
    direction = _rotate(robo.dir, WAY_ANGLE[move_way])
    angle = _angle(move_dir, direction)
    if PRINT:
        print('ang diff:', angle * 180 / math.pi)
    if angle > 0:  # should turn left
        if angle > robo.MOTION['TURN']['LEFT']['BOUND'][0]:
            rt_cmd = robo.MOTION['TURN']['LEFT']['CMD'][0]
            return True, rt_cmd
        elif angle > robo.MOTION['TURN']['LEFT']['BOUND'][1]:
            rt_cmd = robo.MOTION['TURN']['LEFT']['CMD'][1]
            return True, rt_cmd
    else:
        if abs(angle) > robo.MOTION['TURN']['RIGHT']['BOUND'][0]:
            rt_cmd = robo.MOTION['TURN']['RIGHT']['CMD'][0]
            return True, rt_cmd
        elif abs(angle) > robo.MOTION['TURN']['RIGHT']['BOUND'][1]:
            rt_cmd = robo.MOTION['TURN']['RIGHT']['CMD'][1]
            return True, rt_cmd
    '''MOVE'''
    # if the robot is supporter,
    # should give the way of main robot
    if robo.role == Role.INTERFERER or robo.role == Role.ASSISTER:
        chief = None
        for rob in robots:
            if rob.role == Role.STRICKER or robo.role == Role.COUNTER:
                chief = rob
                break
        # if main robot in the neiborhood of support and in the way of the next step
        if chief:
            dist_chief = _dist(robo.pos, chief.pos)
            reserved_dist = 40 * CM_TO_PIX  # safe distance
            safe_angle = math.pi / 4  # reserve a sector with 45 degree and 20cm
            if dist > dist_chief and dist_chief < reserved_dist:
                chief_dir = _unit_vector(robo.pos, chief.pos)
                angle = abs(_angle(move_dir, chief_dir))
                if angle < safe_angle:
                    if PRINT:
                        print('supporter pause for the main')
                    rt_cmd = 'N'
                    return True, rt_cmd
    if dist >= robo.MOTION['MOVE'][move_way]['BOUND'][0] * CM_TO_PIX:
        too_close = is_close_ball(robo.pos, direction, robo.MOTION['MOVE'][move_way]['BOUND'][0] * CM_TO_PIX)
        if (not too_close) or move_way == 'BACK':
            rt_cmd = robo.MOTION['MOVE'][move_way]['CMD'][0]
            return True, rt_cmd
    if len(robo.MOTION['MOVE'][move_way]['BOUND']) > 1:
        if dist >= robo.MOTION['MOVE'][move_way]['BOUND'][1] * CM_TO_PIX:
            rt_cmd = robo.MOTION['MOVE'][move_way]['CMD'][1]
            return True, rt_cmd
    if PRINT:
        print('Cant Find proper cmd.....')
    return False, 'N'


def find_way(robo, ideal_dir, ways):
    product = -1
    choose_way = ""
    for way in ways:
        temp_product = _dot(ideal_dir, _rotate(robo.dir, WAY_ANGLE[way]))
        if temp_product > product:
            product = temp_product
            choose_way = way
    return choose_way


def find_aim_point(x, y, goal):
    """
       According to assumed ball position, caculate the best position to aim on the line(GOAL)
       Parameter:
        param1: (x,y) is the assumed point of ball
        param1: goal[[x1,y1], [x2, y2]] (y1<y2, x1=x2)
       Return:
        retva1: the best point to aim
        retval: the tolerant size
    """
    size = 0
    if goal[0][1] > goal[1][1]:
        temp = goal[1]
        goal[1] = goal[0]
        goal[0] = temp

    aim_point = [goal[0][0], -1]
    enemies_pos = [enemy.pos for enemy in enemies]
    for robo in robots:
        if x < robo.pos[0] <= goal[0][0] or x > robo.pos[0] >= goal[0][0]:
            enemies_pos.append(robo.pos)
    for enemy in enemies_pos:
        if not enemy:
            enemies_pos.remove([])
    if enemies_pos:
        if PRINT:
            print('enemies_pos:', enemies_pos)
        try:
            enemies_pos.sort(key=takeY)
        except Exception:
            print(enemies_pos)
    head_tails = []  # store the areas that are blocked
    for enemy in enemies_pos:
        if x < enemy[0] <= goal[0][0] or x > enemy[0] >= goal[0][0]:
            pair = []
            dir_x = enemy[0] - x
            dir_y = (enemy[1] - ROB_RANG) - y
            pair.append(y + (goal[0][0] - x) / dir_x * dir_y)
            dir_y = (enemy[1] + ROB_RANG) - y
            pair.append(y + (goal[0][0] - x) / dir_x * dir_y)
            head_tails.append(pair)
    # if the blocked areas are consectutive, merge them;
    # if the whole area is beyond border then delete it
    j = 0
    while j < (len(head_tails) - 1):
        if head_tails[j][1] >= head_tails[j + 1][0]:
            head_tails[j][1] = head_tails[j + 1][1]
            del head_tails[j + 1]
        else:
            j += 1
    j = 0
    while j < len(head_tails):
        if head_tails[j][1] <= goal[0][1] or head_tails[j][0] >= goal[1][1]:
            del head_tails[j]
        else:
            j += 1
    # Map non-blocked areas, and find the biggest area
    if PRINT:
        for h_t in head_tails:
            print('ht', h_t)
        print('goal:', goal)
    ava_range = []
    sizes = []
    dists = []
    point = [goal[0][0], -1]
    points = []
    if len(head_tails) == 0:
        sizes.append(goal[1][1] - goal[0][1])
        point[1] = (goal[1][1] + goal[0][1]) / 2
        points.append(point[:])
        dists.append(_dist([x, y], point))
        ava_range.append(goal)
    if len(head_tails) > 0 and head_tails[0][0] - goal[0][1] > size:
        sizes.append(head_tails[0][0] - goal[0][1])
        point[1] = (head_tails[0][0] + goal[0][1]) / 2
        dists.append(_dist([x, y], point))
        points.append(point[:])
        ava_range.append([goal[0][1], head_tails[0][0]])
    for i in range(len(head_tails) - 1):
        if head_tails[i + 1][0] - head_tails[i][1] > size:
            sizes.append(head_tails[i + 1][0] - head_tails[i][1])
            point[1] = (head_tails[i + 1][0] + head_tails[i][1]) / 2
            points.append(point[:])
            dists.append(_dist([x, y], point))
            ava_range.append([head_tails[i][1], head_tails[i + 1][0]])
    if len(head_tails) > 0 and goal[1][1] - head_tails[len(head_tails) - 1][1] > size:
        sizes.append(goal[1][1] - head_tails[len(head_tails) - 1][1])
        point[1] = (goal[1][1] + head_tails[len(head_tails) - 1][1]) / 2
        points.append(point[:])
        # if PRINT:
        #     print('pts', points)
        dists.append(_dist([x, y], point))
        ava_range.append([head_tails[len(head_tails) - 1][1], goal[1][1]])
    # if PRINT:
    #     for i in range(len(sizes)):
    #         print('reange:', ava_range[i])
    #         print('s, pt:,', sizes[i], point[i])
    if sizes:
        size_max = max(sizes)
        dist_max = max(dists)
        comp = -1.1
        for i in range(len(sizes)):
            temp_comp = sizes[i] / size_max - dists[i] / dist_max
            if temp_comp > comp:
                comp = temp_comp
                aim_point = points[i]
                size = sizes[i]
    if PRINT:
        for pair in ava_range:
            print('available area:', pair[0], pair[1])
        print('(', aim_point[0], ',', aim_point[1], '):', size)
    return aim_point, size


def find_shooting_point(x_pos, segm, goal):
    """
       Divide line x='x' into 'segm' segments, and find which one is the best shooting position
       Parameter:
        param1: assign the lin x = 'x' to be examined
        param2: the degree of segmentation
        param3: goal[[x1,y1], [x2, y2]] (y1<y2, x1=x2)
       Return:
        retval1: the best shooting position(next moving point)
        retval2: the best point to aim
        retval3: the tolerant size
    """
    biggest_size = 0
    shooting_pt = []
    aim_pos = []
    for i in range(1, segm):
        x = x_pos
        y = BOUNDARY[0][1] + (BOUNDARY[7][1] - BOUNDARY[0][1]) / segm * i
        aim, size = find_aim_point(x, y, goal)
        if size > biggest_size:
            biggest_size = size
            shooting_pt = [x, y]
            aim_pos = aim
    return shooting_pt, aim_pos, biggest_size


def check_boundary_ball(robo):
    bdry_rang = 12 * CM_TO_PIX
    if ball.pos[1] < BOUNDARY[0][1] + bdry_rang:
        if PRINT:
            print('boundary ball')
        robo.target[0] = ball.pos[0] + SIDE * 15
        robo.target[1] = ball.pos[1] - 15
    elif ball.pos[1] > BOUNDARY[7][1] - bdry_rang:
        if PRINT:
            print('boundary ball')
        robo.target[0] = ball.pos[0] + SIDE * 15
        robo.target[1] = ball.pos[1] + 15


def is_close_ball(pos, direction, len):
    safe_dist = (10 + ball.radius) * CM_TO_PIX
    the_next = [p + d * len for p, d in zip(pos, direction)]
    if _dist(the_next, ball.pos) < safe_dist:
        return True
    return False


def change_robots(newID):
    global robots
    for robo, ID in zip(robots, newID):
        robo.MOTION = CONST.getMotion(ID)


'''end'''


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
        self.in_zone = Zone.NONE
        self.howclose = CONST.TREATING_ZONE * CM_TO_PIX  # minimum distance to judge shooting
        self.face_ball = False  # 注意防守時候須不需要面向敵人
        self.MOTION = CONST.getMotion(ID)
        self.BODY = CONST.getBody()
        self.miss = False

    def move_and_kick(self, carry, target):  # define how to get place and kick ball
        if self.distance > self.howclose:
            self.next = [ball.pos[0] - SIDE * int(8 * CM_TO_PIX), ball.pos[1]]  # 等於球後方一些的位置->向球走過去
            self.job = Job.MOVE  # go go go
        else:
            self.job = Job.PASS  # pass toward
            self.target = [int(target[0]), int(target[1])]  # pass toward

    def find_pass_point(self):
        pass_point = [[self.pos[0] + 75 * CM_TO_PIX * SIDE, ball.pos[1] + 45 * CM_TO_PIX],
                      [self.pos[0] + 75 * CM_TO_PIX * SIDE, ball.pos[1] - 45 * CM_TO_PIX]]
        if pass_point[1][1] < BOUNDARY[0][1] + 22 * CM_TO_PIX:
            pass_point[1][1] = BOUNDARY[0][1] + 22 * CM_TO_PIX
        elif pass_point[0][1] > BOUNDARY[7][1] - 22 * CM_TO_PIX:
            pass_point[0][1] = BOUNDARY[7][1] - 22 * CM_TO_PIX
        return pass_point

    def move_and_block(self):
        if get_distance(self.next, self.pos) > 6 * CM_TO_PIX:
            self.job = Job.MOVE
        else:
            self.job = Job.NONE

    def move_and_do(self, angle_condition, tolerance_angle):
        if get_distance(self.pos, self.next) > 5 * CM_TO_PIX:
            if self.job == Job.REST:
                pass
            else:
                self.job = Job.MOVE
                # print(self.pos, self.next)
                # print(get_distance(self.pos, self.next))
                # print("keeper move!")
        else:
            if angle_condition > tolerance_angle / 180 * math.pi:
                self.job = Job.STAND
                self.face_ball = True
                print("keeper spin!!")
            else:
                self.job = Job.REST
                print("keeper rest~")

    def keeper_assign(self, mode):
        # 戰略：1判斷球的速度，如果是在危險區域之內判斷方向後直接撲球
        #      2中央區站位為正中間
        #      3左邊/右邊的站位都是底線＋球門正中心連線
        #      4球的速度降低後便會出來踢球（如果是最近的）
        #      5沒事多休息
        global ball, enemies
        gate_center = [our_gate[0][0], int((our_gate[0][1] + our_gate[1][1]) / 2)]
        angle_condition = abs(_angle(self.dir, [b - p for b, p in zip(ball.pos, self.pos)]))
        carry = False  # bool of enemy whether carries ball
        self.face_ball = True
        self.next = [gate_center[0] + 13 * CM_TO_PIX * SIDE, gate_center[1]]  # default next position
        for i in range(3):
            if enemies[i].carrier:
                carry = True
                print("enemy carry, in danger!!")
        pass_point = self.find_pass_point()
        if mode == Mode.OFFENSE:
            # print("i can have rest woooo")
            self.move_and_do(angle_condition, 15)
        elif mode == Mode.DEFENSE:
            if ball.speed > CONST.DANGER_SPEED and ball.dir[0] * SIDE < 0:
                self.job = Job.DIVE
                print("ready to dive")
            else:
                if ball.in_zone == Zone.MIDDLE_DEFEND:
                    self.move_and_do(angle_condition, 10)
                    self.job = Job.STAND
                    # print("come from middle , watch out!")
                elif ball.in_zone == Zone.CENTER_AREA:
                    self.move_and_do(angle_condition, 10)
                    self.job = Job.STAND
                    # print("come from middle , watch out!")
                elif ball.in_zone == Zone.LEFT_DEFEND:
                    self.next = line_fraction(gate_center, our_gate[0], 0.4)
                    self.next[0] += 13 * CM_TO_PIX * SIDE
                    self.move_and_do(angle_condition, 12)
                    self.job = Job.STAND
                    # print("come from left , watch out!")
                elif ball.in_zone == Zone.FAR_LEFT_DEFEND:
                    self.next = line_fraction(gate_center, our_gate[0], 0.8)
                    self.next[0] += 13 * CM_TO_PIX * SIDE
                    self.move_and_do(angle_condition, 12)
                    self.job = Job.STAND
                    # print("come from far left , watch out!")
                elif ball.in_zone == Zone.RIGHT_DEFEND:
                    self.next = line_fraction(gate_center, our_gate[1], 0.4)
                    self.next[0] += 13 * CM_TO_PIX * SIDE
                    self.move_and_do(angle_condition, 12)
                    self.job = Job.STAND
                # print("come from right , watch out!")
                elif ball.in_zone == Zone.FAR_RIGHT_DEFEND:
                    self.next = line_fraction(gate_center, our_gate[1], 0.8)
                    self.next[0] += 13 * CM_TO_PIX * SIDE
                    self.move_and_do(angle_condition, 12)
                    self.job = Job.STAND
                    # print("come from far right , watch out!")
                elif ball.in_zone == Zone.OUR_PENALTY:
                    target, size = find_aim_point(ball.pos[0], ball.pos[1], pass_point)
                    if target[1] == -1:
                        target[1] = self.pos[1]
                    self.move_and_kick(carry, target)
                    self.target = target
                    self.job = Job.SHOOT
                    # print("in penalty zone!!!")
                    pass
                else:
                    self.job = Job.STAND
                if carry:
                    self.job = Job.STAND
                    print("ready for battle")
        if PRINT:
            print("keeper next", self.next)

    def stricker_assign(self, other):
        # 戰略：1如果是在中間（非對方進攻位置）直接站到球的後面往前踢，如果空間不夠->射門？？？
        #      2如果是中間/偏左/偏右的位置，直接大暴射門
        #      3如果是極左/極右，往隊友身上傳
        #      5其他情形就直接站在球的正前方，並且射爆
        global robots, ball, carrier_range
        carry = None
        pass_point = self.find_pass_point()
        gate_center = [enemy_gate[0][0], (enemy_gate[0][1] + enemy_gate[1][1]) / 2]
        self.next = [ball.pos[0] - SIDE * int(ball.radius * CM_TO_PIX + 15), ball.pos[1]]
        tar, size = find_aim_point(ball.pos[0], ball.pos[1], [enemy_gate[0], enemy_gate[1]])
        if PRINT:
            print("ball in_zone:", ball.in_zone)
        for i in range(3):
            if enemies[i].carrier:
                carry = i
        if (ball.in_zone == Zone.CENTER_AREA) | ((self.pos[0] - CENTER[0]) * SIDE > 0):  # outside the attack region
            Target, size = find_aim_point(ball.pos[0], ball.pos[1], pass_point)
            if Target[1] == -1:
                Target[1] = self.pos[1]
            self.move_and_kick(carry, Target)
        elif ball.in_zone == Zone.MIDDLE_OFFENCE:
            self.move_and_kick(carry, tar)
            if self.job == Job.PASS:
                self.job = Job.SHOOT  # 可能需要被 override 掉
        elif ball.in_zone == Zone.LEFT_OFFEND:
            # print("left")
            self.move_and_kick(carry, tar)
            if self.job == Job.PASS:
                self.job = Job.SHOOT  # 可能需要被 override 掉
        elif ball.in_zone == Zone.RIGHT_OFFEND:
            # print("right")
            self.move_and_kick(carry, tar)
            if self.job == Job.PASS:
                self.job = Job.SHOOT  # 可能需要被 override 掉
            # print(self.target, size, ball.pos[0], ball.pos[1], [enemy_gate[0], enemy_gate[1]])
        elif ball.in_zone == Zone.FAR_LEFT_OFFEND:
            # print("far_l")
            percent = size / abs((enemy_gate[1][1] - enemy_gate[0][1]) * SIDE)
            # print("percent", percent)
            if (percent < 0.3) & (not robots[other].miss):
                self.move_and_kick(carry, robots[other].next)
            else:
                self.move_and_kick(carry, tar)
                if self.job == Job.PASS:
                    self.job = Job.SHOOT  # 可能需要被 override 掉
        elif ball.in_zone == Zone.FAR_RIGHT_OFFEND:
            # print("fa_r")
            percent = size / abs((enemy_gate[1][1] - enemy_gate[0][1]) * SIDE)
            # print("percent", percent)
            if (percent < 0.3) & (not robots[other].miss):
                self.move_and_kick(carry, robots[other].next)
            else:
                self.move_and_kick(carry, tar)
                if self.job == Job.PASS:
                    self.job = Job.SHOOT  # 可能需要被 override 掉
        else:
            # print("other")
            # don't know how to deal with it , whatever
            self.move_and_kick(carry, tar)
            if self.job == Job.PASS:
                self.job = Job.SHOOT  # 可能需要被 override 掉

    def assister_assign(self, other):
        # 戰略：1如果是在中間（非對方進攻的位置），設定為跟隨模式，跟隨模式為一旦超出邊界，便會站到中央
        #      2如果是中間的位置，站在後方的位置？
        #      3如果是左邊/右邊的位置，站點
        #      4如果是極左/極右的話，不管
        #      5其他也站點，不管
        global ball, enemies, robots
        # print(ball.in_zone)
        if ball.in_zone == Zone.CENTER_AREA:
            if self.half == 'left_side':
                y = robots[other].next[1] - 60 * CM_TO_PIX * SIDE
            else:
                y = robots[other].next[1] + 60 * CM_TO_PIX * SIDE
            if y < BOUNDARY[0][1] + 23 * CM_TO_PIX:  # over boundary, set in center
                y = BOUNDARY[0][1] + 23 * CM_TO_PIX
            elif y > BOUNDARY[7][1] - 23 * CM_TO_PIX:
                y = BOUNDARY[7][1] - 23 * CM_TO_PIX
            self.next = [robots[other].next[0] - 55 * CM_TO_PIX * SIDE, y]  # 暫定距離
            self.move_and_block()
        elif ball.in_zone == Zone.MIDDLE_OFFENCE:
            # print("middle")
            if self.half == 'left_side':
                self.next = [enemy_gate[0][0] - SIDE * 52 * CM_TO_PIX * SIDE,
                             robots[other].next[1] - SIDE * 52 * CM_TO_PIX]
            else:
                self.next = [enemy_gate[1][0] - 52 * CM_TO_PIX * SIDE, robots[other].next[1] - SIDE * 52 * CM_TO_PIX]
            self.move_and_block()
        elif ball.in_zone == Zone.FAR_RIGHT_OFFEND:
            # print("far_r")
            Next = [CENTER[0] + 90 * CM_TO_PIX * SIDE, CENTER[1]]
            for i in range(3):
                if in_line(ball.pos, Next, enemies[i].pos, False):
                    Next = [CENTER[0] + 100 * CM_TO_PIX * SIDE, CENTER[1] + 14 * CM_TO_PIX * SIDE]
            self.move_and_block()
            self.next = Next
        elif ball.in_zone == Zone.FAR_LEFT_OFFEND:
            # print("far_l")
            Next = [CENTER[0] + 90 * CM_TO_PIX * SIDE, CENTER[1]]
            for i in range(3):
                if in_line(ball.pos, Next, enemies[i].pos, False):
                    Next = [CENTER[0] + 100 * CM_TO_PIX * SIDE, CENTER[1] - 14 * CM_TO_PIX * SIDE]
            self.move_and_block()
            self.next = Next
        else:  # 其他直接站定點，先不管了
            # print("other")
            if robots[other].half == "right_side":
                self.next = [enemy_gate[1][0] - 40 * CM_TO_PIX * SIDE, enemy_gate[1][1]]
            elif robots[other].half == "left_side":
                self.next = [enemy_gate[0][0] - 40 * CM_TO_PIX * SIDE, enemy_gate[0][1]]
            self.move_and_block()

    def counter_assign(self):
        # 戰略：1如果是在中間（非對方進攻位置）直接佔到球的後面往前踢
        #      2如果是中間的位置，佔到球和球門中心的連線，略靠近對手
        #      3如果是左邊或是右邊，選擇防守線的邊緣站
        #      4若是滿足2,3的話，便會搶球並踢球
        #      5其他情形就直接站在球的正前方
        #      注意面向方向
        global enemies, ball
        kick_forward = [enemy_gate[0][0], self.pos[1]]
        pass_point = self.find_pass_point()
        gate_side = 1
        if self.half == "left_side":
            gate_side = 0
        carry = None  # index of enemy who carries ball
        self.face_ball = False
        self.next = [ball.pos[0] - SIDE * ((ball.radius + 3) * CM_TO_PIX), ball.pos[1]]  # default next position
        for i in range(3):
            if enemies[i].carrier:
                carry = i
        if (ball.in_zone == Zone.CENTER_AREA) | ((self.pos[0] - CENTER[0]) * SIDE > 0):  # outside the attack region
            Target, size = find_aim_point(ball.pos[0], ball.pos[1], pass_point)
            if Target[1] == -1:
                Target[1] = self.pos[1]
            self.move_and_kick(carry, Target)
        elif ball.in_zone == Zone.MIDDLE_DEFEND:
            if in_line(ball.pos, [our_gate[0][0], (our_gate[0][1] + our_gate[1][1]) / 2], self.pos, False):
                # on defend line , defend line is middle
                self.move_and_kick(carry, kick_forward)
                if PRINT:
                    print("inline\n")
            else:  # move to defend line
                self.next = find_line_point(self.pos, [our_gate[0][0], (our_gate[0][1] + our_gate[1][1]) / 2])
                if (self.next[0] - ball.pos[0] + ball.radius * CM_TO_PIX) * SIDE > 0:
                    self.next = [ball.pos[0] - SIDE * 8 * CM_TO_PIX, ball.pos[1]]
                self.job = Job.MOVE
                if PRINT:
                    print("outline\n")
        elif ball.in_zone == Zone.LEFT_DEFEND:
            if in_line(ball.pos, our_gate[gate_side], self.pos, False):  # on defend line , defend line is left
                self.move_and_kick(carry, kick_forward)
                self.face_ball = True
                if PRINT:
                    print("inline\n")
            else:  # move to defend line
                self.next = find_line_point(self.pos, our_gate[gate_side])
                if (self.next[0] - ball.pos[0] - ball.radius * CM_TO_PIX) * SIDE > 0:
                    self.next = [ball.pos[0] - SIDE * 8 * CM_TO_PIX, ball.pos[1]]
                # self.next[1] += int(SIDE * 8 * CM_TO_PIX)
                self.job = Job.MOVE
                if PRINT:
                    print("outline\n")
        elif ball.in_zone == Zone.FAR_LEFT_DEFEND:
            if in_line(ball.pos, our_gate[gate_side], self.pos, False):  # on defend line , defend line is left
                self.move_and_kick(carry, kick_forward)
                self.face_ball = True
                if PRINT:
                    print("inline\n")
            else:  # move to defend line
                self.next = find_line_point(self.pos, our_gate[gate_side])
                if (self.next[0] - ball.pos[0] - ball.radius * CM_TO_PIX) * SIDE > 0:
                    self.next = [ball.pos[0] - SIDE * 8 * CM_TO_PIX, ball.pos[1]]
                # self.next[1] += int(SIDE * 8 * CM_TO_PIX)
                self.job = Job.MOVE
        elif ball.in_zone == Zone.FAR_RIGHT_DEFEND:
            if in_line(ball.pos, our_gate[gate_side], self.pos, False):  # on defend line , defend line is right
                self.move_and_kick(carry, kick_forward)
                if PRINT:
                    print("inline\n")
            else:  # move to defend line
                self.next = find_line_point(self.pos, our_gate[gate_side])
                if (self.next[0] - ball.pos[0] - ball.radius * CM_TO_PIX) * SIDE > 0:
                    self.next = [ball.pos[0] - SIDE * 8 * CM_TO_PIX, ball.pos[1]]
                # self.next[1] += int(SIDE * 8 * CM_TO_PIX)
                self.job = Job.MOVE
                self.face_ball = True
        elif ball.in_zone == Zone.RIGHT_DEFEND:
            if in_line(ball.pos, our_gate[gate_side], self.pos, False):  # on defend line , defend line is right
                self.move_and_kick(carry, kick_forward)
                if PRINT:
                    print("inline\n")
            else:  # move to defend line
                self.next = find_line_point(self.pos, our_gate[gate_side])
                if (self.next[0] - ball.pos[0] - ball.radius * CM_TO_PIX) * SIDE > 0:
                    self.next = [ball.pos[0] - SIDE * 8 * CM_TO_PIX, ball.pos[1]]
                # self.next[1] -= int(SIDE * 8 * CM_TO_PIX)
                self.job = Job.MOVE
                self.face_ball = True
        else:
            if self.half == "right_side":
                self.next = our_gate[3]
            else:
                self.next = our_gate[2]
            self.move_and_block()
        if robots[2].job == Job.DIVE or robots[2].job == Job.SHOOT:
            self.job = Job.NONE
        if get_distance(self.next, robots[2].pos) > 28 * CM_TO_PIX:
            self.next = [self.next[0] + SIDE * 13 * CM_TO_PIX, self.next[1]]

    def interferer_assign(self, other):
        # 戰略：1如果是在中間（非對方進攻的位置），設定為跟隨模式，跟隨模式為一旦超出邊界，便會站到中央
        #      2如果是中間的位置，看位置是左邊還是右邊直接站定點
        #      3如果是左邊或是右邊，靠防守線站立
        #      4若是滿足2,3的話，不做任何事情，蹲下休息
        #      5其他情形就直接站在球後方
        #      如果另一隻機器人不在自動變成進攻者
        global robots, ball
        self.face_ball = False
        self.target = [0, 0]
        if (ball.in_zone == Zone.CENTER_AREA) | ((robots[other].pos[0] - CENTER[0]) * SIDE > 0):
            if self.half == 'left_side':
                y = robots[other].next[1] - 60 * CM_TO_PIX * SIDE
            else:
                y = robots[other].next[1] + 60 * CM_TO_PIX * SIDE
            if y < BOUNDARY[0][1] + 23 * CM_TO_PIX:  # over boundary, set in center
                y = BOUNDARY[0][1] + 23 * CM_TO_PIX
            elif y > BOUNDARY[7][1] - 23 * CM_TO_PIX:
                y = BOUNDARY[7][1] - 23 * CM_TO_PIX
            self.next = [robots[other].next[0] - 55 * CM_TO_PIX * SIDE, y]  # 暫定距離
            self.move_and_block()
        elif ball.in_zone == Zone.MIDDLE_DEFEND:
            if self.half == 'left_side':
                self.next = [our_gate[0][0] + SIDE * 30 * CM_TO_PIX, our_gate[0][1] + 5 * CM_TO_PIX * SIDE]
            else:
                self.next = [our_gate[1][0] + SIDE * 30 * CM_TO_PIX, our_gate[1][1] - 5 * CM_TO_PIX * SIDE]
            self.move_and_block()
        elif ball.in_zone == Zone.FAR_LEFT_DEFEND:
            if in_line(ball.pos, our_gate[1], self.pos, False):  # on defend line , defend line is right
                self.face_ball = True
                self.job = Job.REST
            else:  # move to defend line
                self.next = line_fraction(ball.pos, our_gate[1], 0.75)  # gate_right
                self.move_and_block()
                # print(self.next)
        elif ball.in_zone == Zone.LEFT_DEFEND:
            if in_line(ball.pos, our_gate[1], self.pos, False):  # on defend line , defend line is right
                self.face_ball = True
                self.job = Job.STAND
            else:  # move to defend line
                self.next = line_fraction(ball.pos, our_gate[1], 0.75)
                self.job = Job.MOVE
                # print(self.next)
        elif ball.in_zone == Zone.FAR_RIGHT_DEFEND:
            if in_line(ball.pos, our_gate[0], self.pos, False):  # on defend line , defend line is left
                self.face_ball = True
                self.job = Job.REST
            else:  # move to defend line
                self.next = line_fraction(ball.pos, our_gate[0], 0.75)  # gate_left
                self.job = Job.MOVE
        elif ball.in_zone == Zone.RIGHT_DEFEND:
            if in_line(ball.pos, our_gate[0], self.pos, False):  # on defend line , defend line is left
                self.face_ball = True
                self.job = Job.REST
            else:  # move to defend line
                self.next = line_fraction(ball.pos, our_gate[0], 0.75)  # gate_left
                self.job = Job.MOVE
        else:
            if self.half == "right_side":
                self.next = our_gate[3]
            else:
                self.next = our_gate[2]
            self.move_and_block()

        if robots[2].job == Job.DIVE or robots[2].job == Job.SHOOT:
            self.job = Job.NONE
        if get_distance(self.next, robots[2].pos) > 28 * CM_TO_PIX:
            self.next = [self.next[0] + SIDE * 13 * CM_TO_PIX, self.next[1]]

    def roamer_assign(self):
        print('no job assign?')
        self.job = Job.STAND
        pass


class Enemy:
    def __init__(self):
        self.pos = [0, 0]
        # self.half = 'middle_side'
        self.distance = 1000  # distance between robot and ball
        self.carrier = False  # who is carry ball
        self.in_zone = Zone.NONE
        self.miss = True


class Ball:
    def __init__(self):
        self.pos = [0, 0]
        self.speed = 0  # speed rank
        self.dir = [0, 0]
        self.status = 'free'
        self.radius = CONST.BALL_RADIUS
        self.in_zone = Zone.NONE


class Role(Enum):
    ROAMER = 0  # 無分配
    KEEPER = 1  # 守門
    COUNTER = 2  # 反擊者
    INTERFERER = 3  # 干擾者
    STRICKER = 4  # 主進攻者
    ASSISTER = 5  # 助攻者


class Job(Enum):
    STAND = 0  # 站定位
    MOVE = 1  # 移動到定點
    PASS = 2  # 傳球
    ACCURATE_SHOOT = 3
    # SET_ANGLE = 4  # 喬角度
    SHOOT = 5  # 射門
    # SQUEEZE = 6  # 推擠（針對持球球員）
    # BLOCK = 7  # 阻止進球
    DIVE = 8  # 撲球
    REST = 9  # 蹲下
    NONE = 10


class Mode(Enum):
    OFFENSE = 0
    DEFENSE = 1
    #  CHEERED = 2


class Zone(Enum):
    NONE = -1
    OUR_PENALTY = 0
    ENEMY_PENALTY = 1
    LEFT_DEFEND = 2
    RIGHT_DEFEND = 3
    FAR_LEFT_DEFEND = 4
    FAR_RIGHT_DEFEND = 5
    MIDDLE_DEFEND = 6
    CENTER_AREA = 7
    LEFT_OFFEND = 8
    RIGHT_OFFEND = 9
    FAR_LEFT_OFFEND = 10
    FAR_RIGHT_OFFEND = 11
    MIDDLE_OFFENCE = 12


if __name__ == '__main__':
    Initialize()
