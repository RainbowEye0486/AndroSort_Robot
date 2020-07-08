import math
from Strategy import constant1 as CONST
from enum import Enum
import time
from threading import Timer

# Parameter needed to adjust
ID_IN_USE = [4, 1]
PRINT = True

# Field Parameter
CM_TO_PIX = 3.0
BOUNDARY = []
CENTER = [0, 0]
PENALTY = 0
SIDE = 1  # left is our field
FB_X = 0
GOAL = []
#  
robots = []
enemies = []
ball = None
ROB_RANG = 40  # 12cm = 40pixel
last_ball = []
ball_in_move = []
record_ball = False
start_pass = False
job_done = False  # for sup
job_start = False  # for main
sec_pt = []
shoot_zone = 0 * CM_TO_PIX
best_loc = [0, 0]
x_offst = 35 * CM_TO_PIX
y_offst = -35 * CM_TO_PIX
our_gate = []
leave_at = []
# CONST
WAY_ANGLE = {'FORE': 0, 'LEFT': -math.pi / 2, 'RIGHT': math.pi / 2, 'BACK': math.pi}


def restart():
    global record_ball, start_pass
    record_ball = False
    start_pass = False
    for robo in robots:
        robo.role = ''
    print('restart')


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
        param5: int -> x coordinate of free ball point w.r.t center
    """
    # Your code
    global SIDE, BOUNDARY, CENTER, GOAL, our_gate
    SIDE = side
    BOUNDARY = boundary
    CENTER = center
    GOAL = [BOUNDARY[2], BOUNDARY[5]] if SIDE == 1 else [BOUNDARY[11], BOUNDARY[8]]
    our_gate = [BOUNDARY[11], BOUNDARY[8]] if SIDE == 1 else [BOUNDARY[2], BOUNDARY[5]]
    if PRINT:
        print('GOAL:', GOAL)


def Initialize():
    """
    Description:
        Initialise the strategy.
        This function will be called by the simulator before a simulation is started.
    """
    if PRINT:
        print('initialize')
    global robots, enemies, ball
    for i in range(2):
        robots.append(Robot(ID_IN_USE[i]))
    for i in range(2):
        enemies.append([])
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
    return frame


def Update_Robo_Info(teamD, teamP, oppoP, ballP, ballS=0, ballD=[0, 0]):
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
        param4: int -> ball speed
        pa
    """
    # Your code
    for i in range(2):
        if teamP[i]:
            robots[i].pos = teamP[i]
        if teamD[i]:
            robots[i].dir = teamD[i]
        if oppoP[i]:
            enemies[i] = oppoP[i]
    if ballP:
        ball.pos = ballP
    if PRINT:
        print('enemy', enemies)
    # ball.sped = ballS
    # return False


def strategy():
    """
    Description:
        The simulator will ask for strategy after calling Update_Robo_Info()
    Return:
        retva1: str -> command for this robot
    """
    # Your code
    global robots, last_ball, record_ball, ball_in_move, leave_at
    # robots[1].job = Job.SHOOT
    # robots[1].target, size = find_aim_point(ball.pos[0], ball.pos[1], GOAL)
    # print('aim', robots[1].target, size/(GOAL[0][1]-GOAL[1][1]))

    if not record_ball:
        last_ball = ball.pos
        ball_in_move = ball.pos
        leave_at = [robots[0].pos[0]-SIDE*15*CM_TO_PIX, robots[0].pos[1]]
        best_loc[0] = CENTER[0] + SIDE*x_offst
        best_loc[1] = CENTER[1] + SIDE*y_offst
        record_ball = True
    assign_role(robots)
    assign_job(robots)
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


def assign_role(robots):
    '''
    Decide every robot's role and change robot's attribute: role
    '''
    if PRINT:
        print('assign role')
    if robots[0].role == '':
        robots[0].role = Role.SUP
        robots[1].role = Role.NONE
        print(robots[0].role, robots[1].role)
    if job_start:
        robots[1].role = Role.MAIN


def assign_job(robots):
    '''
    Decide every robot's job and change robot's attribute: job
    '''
    for robo in robots:
        if robo.role == Role.SUP:
            if job_done:
                robo.job = Job.LEAVE
            else:
                robo.job = Job.MOVE
        elif robo.role == Role.MAIN:
            if (ball.pos[0] - (CENTER[0] + shoot_zone * SIDE)) * SIDE > 0:
                robo.job = Job.SHOOT  # to goal
            else:
                robo.job = Job.MOVE  # to three point line
        elif robo.role == Role.NONE:
            robo.job = Job.REST


def execute_job(id):
    """
    Base on the robot's job, give an exact command
    """
    global robots, sec_pt, job_done
    robo = robots[id]
    if robo.job == Job.MOVE:
        dirct = _unit_vector(ball.pos, best_loc)
        init_pt = [b - d * 15 * CM_TO_PIX for b, d in zip(ball.pos, dirct)]
        global start_pass, ball_in_move
        # print('flag', start_pass)
        if not start_pass:
            sec_pt = [b + d * 3 * CM_TO_PIX for b, d in zip(ball.pos, dirct)]
            dist_err = 2*CM_TO_PIX
            ang_err = 15/180*math.pi
            ball_in_move = ball.pos
            arrival = init_pt
            robo.next = arrival
            move_ways = ['FORE', 'LEFT', 'RIGHT', 'BACK']
            direction = _rotate(robo.dir, WAY_ANGLE['LEFT'])
            movable, rt_cmd = move_with_dir(robo, arrival, direction, dirct, 'LEFT', move_ways)
            if movable and (_dist(robo.pos, arrival) > dist_err or abs(_angle(direction, dirct)) > ang_err):
                return rt_cmd
            else:
                # if ball.speed < 10:
                start_pass = True
        else:
            # for supporter
            if robo.role == Role.SUP:
                if _dist(ball.pos, last_ball) > 12*CM_TO_PIX:
                    job_done = True
                    print(job_done)
                    start_pass = False
                    t = Timer(2.0, startMain)
                    t.start()
            arrival = sec_pt
            robo.next = arrival
            move_ways = ['LEFT']
            movable, rt_cmd = move_special(robo, arrival, move_ways)
            if movable:
                return rt_cmd
            else:
                start_pass = False
                # sec_pt = [-1, -1]
                if PRINT:
                    print('toggle to False')
    elif robo.job == Job.PASS:
        if PRINT:
            print('role, job', robo.role, robo.job)
        if robo.target[0] == -1:
            # x_pos = CENTER[0] + (shoot_zone)*SIDE
            # segm = 4
            # robo.target, no_use, no_use = find_shooting_point(x_pos, segm, GOAL)
            robo.target = best_loc
        check_boundary_ball(robo)
        # kick ball
        if PRINT:
            print(robo.target)
        kickable_dist = 2 * CM_TO_PIX  # the distance between ball and the robot should be
        kickable_ang = 7 / 180 * math.pi  # acceptable angle error when kicking
        kick_ways = ['FORE']
        move_ways = ['FORE', 'LEFT', 'BACK', 'RIGHT']
        try:
            kick_dir = _unit_vector(ball.pos, robo.target)
            force = 'small'
            kickable, kick_way, rt_cmd, arrival = is_kickable(robo, kickable_dist, kickable_ang, kick_dir, kick_ways, force)
            robo.next = arrival  #
        except ZeroDivisionError:
            print("ball has arrived the point")
            kickable = False
        if kickable:
            robo.target = [-1, -1]
            return rt_cmd
        movable, rt_cmd = move_with_dir(robo, arrival, _rotate(robo.dir, WAY_ANGLE[kick_way]), kick_dir, kick_way)
        if movable:
            return rt_cmd
    elif robo.job == Job.SHOOT:
        robo.target, size = find_aim_point(ball.pos[0], ball.pos[1], GOAL)
        print('size:', size/(GOAL[0][1]-GOAL[1][1]))
        check_boundary_ball(robo)
        if not (size > 0):
            if ball.pos[1] - CENTER[1] < 0:  # upper field
                kick_dir = _rotate([0, -1], -1*SIDE*60/180*math.pi)
            else:
                kick_dir = _rotate([0, 1], -1*SIDE*60/180*math.pi)
            robo.target = [b+d*10 for b, d in zip(ball.pos, kick_dir)]
        if robo.target[0] != -1:
            force = 'big'
            kickable_dist = 3*CM_TO_PIX  # the distance between arrival and the robot should be
            kickable_ang = 7/180*math.pi  # acceptable angle error when kicking
            kick_ways = ['LEFT', 'RIGHT']
            move_ways = ['FORE', 'LEFT', 'BACK', 'RIGHT']
            kick_dir = _unit_vector(ball.pos, robo.target)
            kickable, kick_way, rt_cmd, arrival = is_kickable(robo, kickable_dist, kickable_ang, kick_dir, kick_ways,
                                                              force)
            robo.next = arrival  #
            if kickable:
                time.sleep(0.05)
                robo.job = Job.NONE
                robo.target = [-1, -1]
                return rt_cmd
            movable, rt_cmd = move_with_dir(robo, arrival, _rotate(robo.dir, WAY_ANGLE[kick_way]), kick_dir, kick_way,
                                            move_ways)
            if movable:
                return rt_cmd
            if PRINT:
                print('moveable', movable)
    elif robo.job == Job.DRIBBLE:
        pass
    elif robo.job == Job.LEAVE:
        arrival = leave_at
        movable = False
        accurate = False
        movable, rt_cmd = move(robo, arrival, ['FORE', 'LEFT', 'RIGHT', 'BACK'], accurate)
        robo.next = arrival
        if movable and _dist(arrival, robo.pos) > 3*CM_TO_PIX and SIDE*(robo.pos[0]-arrival[0]) > 0:
            return rt_cmd
        else:
            robo.role = Role.NONE
    elif robo.job == Job.REST:
        return robo.MOTION['REST']['CMD'][0]
    return 'N'

'''
   Collection of vector operation in this program
'''

def _dist(pos1, pos2):
    '''return absolute distance between [x1,y1], [x2,y2]'''
    return math.hypot(pos1[0]-pos2[0], pos1[1]-pos2[1])


def _unit_vector(start, end):
    '''return unit vector from start to end'''
    vector = [e - s for s, e in zip(start, end)]
    length = math.hypot(vector[0], vector[1])
    uniVector = [comp/length for comp in vector]
    return uniVector


def _dot(x, y):
    """
       Dot product as sum of list comprehension doing element-wise multiplication
    """
    return sum(x_i*y_i for x_i, y_i in zip(x, y))


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
    '''
       rotate vector by angle(radius) in counterclockwise direction
    '''
    rot_vector = [0.0, 0.0]
    rot_vector[0] = (math.cos(angle)*vector[0]) - (math.sin(angle)*vector[1])
    rot_vector[1] = (math.sin(angle)*vector[0]) + (math.cos(angle)*vector[1])
    return rot_vector


def is_kickable(robo, tol_dist, tol_angle, kick_dir, ways, force):
    # Find kick way(R,L,F,B)
    kick_way = find_way(robo, kick_dir, ways)
    if PRINT:
        print()
        print('====in kickable===')
        print('robo, kick_dir', robo.dir, kick_dir)
        print('kick way:', kick_way)
    arrival = [b - un_dir*ball.RADIUS*CM_TO_PIX for b, un_dir in zip(ball.pos, kick_dir)]
    ver_offst = [direct * -robo.MOTION['MOVE'][kick_way]['OFFSET'][0]*CM_TO_PIX for direct in kick_dir]
    hor_offst = [0, 0]
    if kick_way == 'FORE' or kick_way == 'BACK':
        angle = _angle(robo.dir, [ball - pos for ball, pos in zip(ball.pos, robo.pos)])
        foot = 'RIGHT' if angle > 0 and force == 'big' else 'LEFT'
        direction = _rotate(kick_dir, WAY_ANGLE[foot])
        offst = -robo.MOTION['MOVE'][kick_way]['OFFSET'][1]*CM_TO_PIX if kick_way=='FORE' else  robo.MOTION['MOVE'][kick_way]['OFFSET'][1]*CM_TO_PIX
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
                time.sleep(0.1)
            else:
                time.sleep(0.1)
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
    rt_cmd = 'N'
    tol_dist = 10 * CM_TO_PIX  # start fitting the right direction
    safe_ball = 15 * CM_TO_PIX
    dist = _dist(robo.pos, arrival)
    dist_ball = _dist(robo.pos, ball.pos)
    if PRINT:
        print()
        print('===m w/ dir ===')
        print('dist:', dist / CM_TO_PIX)
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
        if PRINT:
            print('lack', move_way, product / CM_TO_PIX)
        if product >= robo.MOTION['MOVE'][move_way]['BOUND'][0] * CM_TO_PIX:
            too_close = is_close_ball(robo.pos, temp_dir, robo.MOTION['MOVE'][move_way]['BOUND'][0] * CM_TO_PIX)
            if (not too_close) or move_way == 'BACK':
                rt_cmd = robo.MOTION['MOVE'][move_way]['CMD'][0]
                time.sleep(0.2)
            return True, rt_cmd
        if len(robo.MOTION['MOVE'][move_way]['BOUND']) > 1:
            if product >= robo.MOTION['MOVE'][move_way]['BOUND'][1] * CM_TO_PIX:
                rt_cmd = robo.MOTION['MOVE'][move_way]['CMD'][1]
                return True, rt_cmd
    return False, 'N'


def move(robo, arrival, ways=['FORE', 'LEFT', 'RIGHT', 'BACK'], accurate=True):
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
        print('dir:', move_dir)
        print('move way', move_way)
        print('dist', dist)
    # if the robot will pass the ball while moving
    dist_ball = _dist(robo.pos, ball.pos)
    if dist > dist_ball:
        ball_dir = _unit_vector(robo.pos, ball.pos)
        angle = abs(_angle(move_dir, ball_dir))
        if move_way == 'FORE' or move_way == 'BACK':
            avoid_dist = robo.BODY['width']/2*CM_TO_PIX
        else:
            avoid_dist = robo.BODY['length']/2*CM_TO_PIX
        safe_angle = math.atan(avoid_dist/dist_ball)
        if angle < safe_angle:
            # change arrival
            if PRINT:
                print('change arrival')
            product = -1
            re_dir = [0, 0]
            for sign in [-1, 1]:
                temp_dir = _rotate(ball_dir, sign*safe_angle)
                temp_product = _dot(move_dir, temp_dir)
                if temp_product > product:
                    product = temp_product
                    mag = math.sqrt(dist_ball**2 + avoid_dist**2)
                    for i in [0, 1]:
                        re_dir[i] = temp_dir[i]*mag
                        arrival[i] = robo.pos[i] + re_dir[i]
            move_dir = _unit_vector(robo.pos, arrival)
            move_way = find_way(robo, move_dir, ways)
            dist = _dist(robo.pos, arrival)
    # fix angle
    direction = _rotate(robo.dir, WAY_ANGLE[move_way])
    angle = _angle(move_dir, direction)
    if PRINT:
        print('ang diff:', angle*180/math.pi)
    if angle > 0:  # should turn left
        if angle > robo.MOTION['TURN']['LEFT']['BOUND'][0]:
            rt_cmd = robo.MOTION['TURN']['LEFT']['CMD'][0]
            return True, rt_cmd
        elif angle > robo.MOTION['TURN']['LEFT']['BOUND'][1]:
            rt_cmd = robo.MOTION['TURN']['LEFT']['CMD'][1]
            return True, rt_cmd
    else:
        if abs(angle) > robo.MOTION['TURN']['RIGHT']['BOUND'][0] and accurate:
            rt_cmd = robo.MOTION['TURN']['RIGHT']['CMD'][0]
            return True, rt_cmd
        elif abs(angle) > robo.MOTION['TURN']['RIGHT']['BOUND'][1] and accurate:
            rt_cmd = robo.MOTION['TURN']['RIGHT']['CMD'][1]
            return True, rt_cmd
    '''MOVE'''
    # if the robot is supporter,
    # should give the way of main robot
    if robo.role == Role.SUP:
        chief = None
        for rob in robots:
            if rob.role == Role.MAIN:
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
                    rt_cmd = 'N'
                    return True, rt_cmd
    if dist >= robo.MOTION['MOVE'][move_way]['BOUND'][0] * CM_TO_PIX:
        too_close = is_close_ball(robo.pos, direction, robo.MOTION['MOVE'][move_way]['BOUND'][0] * CM_TO_PIX)
        if (not too_close) or move_way == 'BACK':
            rt_cmd = robo.MOTION['MOVE'][move_way]['CMD'][0]
            # time.sleep(0.2)
            return True, rt_cmd
    if len(robo.MOTION['MOVE'][move_way]['BOUND']) > 1:
        if dist >= robo.MOTION['MOVE'][move_way]['BOUND'][1] * CM_TO_PIX and accurate:
            rt_cmd = robo.MOTION['MOVE'][move_way]['CMD'][1]
            return True, rt_cmd
    if PRINT:
        print('Cant Find proper cmd.....')
    return False, 'N'


def move_special(robo, arrival, ways=['FORE', 'LEFT', 'RIGHT', 'BACK']):
    '''
       To move to assigned point and facing whatever direction
    '''
    move_dir = _unit_vector(robo.pos, arrival)
    dist = _dist(robo.pos, arrival)
    move_way = find_way(robo, move_dir, ways)
    if PRINT:
        print()
        print('---->move w/o dir arr:', arrival)
        print('dir:', move_dir)
        print('move way', move_way)
        print('dist', dist)
    # fix angle
    direction = _rotate(robo.dir, WAY_ANGLE[move_way])
    angle = _angle(move_dir, direction)
    if PRINT:
        print('ang diff:', angle*180/math.pi)
    if angle > 0:  # should turn left
        if angle > robo.MOTION['TURN']['LEFT']['BOUND'][0]:
            rt_cmd = robo.MOTION['TURN']['LEFT']['CMD'][0]
            return True, rt_cmd
        # elif angle > robo.MOTION['TURN']['LEFT']['BOUND'][1]:
        #     rt_cmd = robo.MOTION['TURN']['LEFT']['CMD'][1]
        #     return True, rt_cmd
    else:
        if abs(angle) > robo.MOTION['TURN']['RIGHT']['BOUND'][0]:
            rt_cmd = robo.MOTION['TURN']['RIGHT']['CMD'][0]
            return True, rt_cmd
        # elif abs(angle) > robo.MOTION['TURN']['RIGHT']['BOUND'][1]:
        #     rt_cmd = robo.MOTION['TURN']['RIGHT']['CMD'][1]
        #     return True, rt_cmd
    '''MOVE'''
    # if dist >= robo.MOTION['MOVE'][move_way]['BOUND'][0] * CM_TO_PIX:
    #     # too_close = is_close_ball(robo.pos, direction, robo.MOTION['MOVE'][move_way]['BOUND'][0] * CM_TO_PIX)
    #     # if (not too_close) or move_way == 'BACK':
    #     rt_cmd = robo.MOTION['MOVE'][move_way]['CMD'][0]
    #     time.sleep(0.2)
    #     return True, rt_cmd
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
    # if PRINT:
    #     print('====find aim===')
    aim_point = [goal[0][0], -1]
    size = 0
    enemies_pos = enemies[:]
    for enemy in enemies_pos:
        if not enemy:
            enemies_pos.remove([])
    if enemies_pos:
        enemies_pos.sort(key=takeY)  # ??
    head_tails = []  # store the areas that are blocked
    # if PRINT:
    #     print('enenies_pos', enemies_pos)
    #     print('ball(', x, y, ')')
    #     print('goal:', goal)
    for enemy in enemies_pos:
        if enemy:
            # if PRINT:
            #     print('enemy', enemy)
            if x < enemy[0] <= goal[0][0] or x > enemy[0] >= goal[0][0]:
                # if PRINT:
                #     print('between')
                pair = []
                dir_x = enemy[0] - x
                dir_y = (enemy[1] - ROB_RANG) - y
                pair.append(y + (goal[0][0] - x) / dir_x * dir_y)
                dir_y = (enemy[1] + ROB_RANG) - y
                pair.append(y + (goal[0][0] - x) / dir_x * dir_y)
                head_tails.append(pair)
    # if PRINT:
    #     print('head_tail', head_tails)
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
            temp_comp = sizes[i]/size_max - dists[i]/dist_max
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
        y = BOUNDARY[0][1]+(BOUNDARY[7][1] - BOUNDARY[0][1])/segm*i
        aim, size = find_aim_point(x, y, goal)
        if size > biggest_size:
            biggest_size = size
            shooting_pt = [x, y]
            aim_pos = aim
    return shooting_pt, aim_pos, biggest_size


def takeY(e):
    return e[1]


def is_close_ball(pos, direction, len):
    safe_dist = (9 + ball.RADIUS) * CM_TO_PIX
    the_next = [p + d * len for p, d in zip(pos, direction)]
    if _dist(the_next, ball.pos) < safe_dist:
        return True
    return False


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


def startMain():
    global job_start
    job_start = True



class Robot:
    """
    Attributes:
        ID: An int stands for the robot's ID(1-7)
        pos: An list[x,y] stands for the robot's position
        dir: list[x,y] -> The direction the robot faces, stored in unit vector
        role: A Role(Enum) represents the robot's role
        job: A Job(Enum) -> the move the robots are going to execute
        MOTION: motion contants from constant.py
        BODY: robot size from constant.py
    """

    def __init__(self, ID):
        self.ID = ID
        self.pos = [-1, -1]
        self.dir = [0, 0]
        self.role = ''
        self.job = Job.NONE
        self.MOTION = CONST.getMotion(ID)
        self.BODY = CONST.getBody()
        self.target = [-1, -1]
        self.next = [-1, -1]


class Role(Enum):
    NONE = 0
    MAIN = 1  # attacker or defender
    SUP = 2  # supporter
    GK = 3


class Job(Enum):
    NONE = 0
    MOVE = 1
    PASS = 2
    SHOOT = 3
    DRIBBLE = 4
    LEAVE = 5
    REST = 6


# class Enemy():
#     def __init__(self):
#         self.pos = [0, 0]


class Ball:
    def __init__(self):
        self.pos = [0, 0]
        self.RADIUS = CONST.getRadius()


if __name__ == '__main__':
    pass