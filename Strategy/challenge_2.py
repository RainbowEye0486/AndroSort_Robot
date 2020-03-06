import math
import cv2
from time import sleep

# Const
ROB_RANG = 25
KICKABLE_RANGE = 40
ROUGH_RANG = 50
ERROR_DISTANCE = 10
ROTATE_ANGLE = 0.30
SAFE_DIST = 43  # RoboRad/2 + ball radius
WAY_ANGLE = {'F': 0, 'L': -math.pi/2, 'R': math.pi/2}
MOVE = {
    'F': {'Fast': 'W1', 'Norm': 'w1', 'Bound': [18, 10]},
    'L': {'Fast': 'A1', 'Norm': 'a1', 'Kick': 'h1', 'Bound': [80, 8]},
    'R': {'Fast': 'D1', 'Norm': 'd1', 'Kick': 'j1', 'Bound': [80, 8]},
    'B': {'Norm': 's1', 'Bound': [None, 10]}
}
# Condition
ALLOW_MOVE_WAY = ['L', 'R']
# Field Variable
BOUNDARY = []  # [(x, y), ...]
CENTER = (0, 0)
ori_center = []
ga_x = ga_y = 0

# Ball, Robot Parameter

ball_p = [0, 0]
player_id = 0
player_p = [0, 0]
player_d = [0.0, 0.0]
oppo_id = 3
oppo_p = [0, 0]

# Anticipate point

stage = 0
kick_goal = [0, 0]
kick_dir = [0.0, 0.0]
first_arri = [0, 0]
kick_point = [0, 0]
kick_p = [0, 0]
kick_d = [0.0, 0.0]
kick_way = ""
move_way = ""
move_dir = [0.0, 0.0]
toward_dir = [0.0, 0.0]
kick_flag = False
kicked = False


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
    global BOUNDARY, ori_center
    ori_center = center
    for pos in boundary:
        BOUNDARY.append((pos[0], pos[1]))

    pass


def Initialize():
    """
    Description:
        Initialise the strategy.
        This function will be called by the simulator before a simulation is started.
    """
    # Your code
    print("Your Player is Robot", player_id)
    print("Obstacle is Robot", oppo_id)
    global stage 
    stage = 1
    # output stratgy
    with open('strategy.txt', 'a') as f:
        f.write('\n')
        f.write('New strategy(pos3 3): ')
    pass


def draw_on_simulator(frame):
    """
    Description:
        Draw whatever you want on the simulator.
        Before the simulator update window, it will call this function and you can just draw anything you want.
        This function will be called every time the simulator is going to update frame.
    Parameter:
        param1: numpy array -> the frame that will be displayed
    Return:
        retva1: numpy array -> the frame that will be displayed
    """
    # Your code
    if stage > 1:
        cv2.circle(frame, (int(first_arri[0]), int(first_arri[1])), 3, (237, 183, 217), -1)
        cv2.line(frame, (ball_p[0], ball_p[1]), (kick_goal[0], kick_goal[1]), (0, 0, 255), 2)
        cv2.circle(frame, (int(player_p[0]), int(player_p[1])), 3, (0, 0, 255), -1)
    if stage > 2:
        cv2.circle(frame, (int(kick_point[0]), int(kick_point[1])), 3, (232, 122, 63), -1)
    return frame


def Update_Robo_Info(teamD, teamP, oppoP, ballP):
    """
    Description:
        Pass robot and ball info into strategy.
        This function will be called before every time the simulator ask for strategy
    Parameter:
        param1: list[list[float]] -> [x,y] for our teammate robot direction
        param2: list[list[int]] -> [x,y] for our teammate robot position
        param3: list[list[int]] -> [x,y] for opponent's robot position
        param4: list[int] -> [x,y] for ball position
    """
    # Your code
    global player_d, player_p, player_id, oppo_id, oppo_p, ball_p
    player_d = teamD[player_id]
    player_p = teamP[player_id]
    oppo_p = oppoP[oppo_id-3]
    ball_p = ballP

    pass


def strategy():
    """
    Description:
        The simulator will ask for strategy after calling Update_Robo_Info()
    Return:
        retva1: list[str] -> command for each robot
    """
    global stage, kick_way, move_way, first_arri, kick_dir, kick_point
    # Your code
    if stage == 1:
        # Find position of goal
        kick_goal[0] = BOUNDARY[2][0]
        allow = [BOUNDARY[2][1], BOUNDARY[5][1]] \
            if BOUNDARY[2][1] < BOUNDARY[5][1] else [BOUNDARY[5][1], BOUNDARY[2][1]]
        block = []
        block.append(oppo_p[1] - ROB_RANG)
        block.append(oppo_p[1] + ROB_RANG)
        if block[0] > allow[0]:
            if block[1] < allow[-1]:
                allow.insert(1, block[0])
                allow.insert(2, block[1])
            else:
                allow[1] = block[0]
        else:
            allow[0] = block[1]
        dist = None
        for i in range(0, len(allow), 2):
            if allow[i+1] - allow[i] > KICKABLE_RANGE:
                kick_goal_temp = int((allow[i] + allow[i+1]) / 2)
                if dist is None or dist > abs(ball_p[1] - kick_goal_temp):
                    dist = abs(ball_p[1] - kick_goal_temp)
                    kick_goal[1] = kick_goal_temp
        print('Goal(x y)', kick_goal[0], kick_goal[1])
        global kick_dir
        kick_dir = _unit_vector(ball_p, kick_goal)
        print(kick_dir)
        global first_arri, kick_point
        first_arri = [int(ball_p[i]-kick_dir[i]*ROUGH_RANG) for i in range(2)]
        kick_point = [int(ball_p[i]-kick_dir[i]*SAFE_DIST) for i in range(2)]
        # Find the way of move
        move_dir = _unit_vector(player_p, first_arri)
        product = -1
        for way in ALLOW_MOVE_WAY:
            temp_product = _dot(move_dir, _rotate(player_d, WAY_ANGLE[way]))
            print(way, ':', temp_product, move_dir, _rotate(player_d, WAY_ANGLE[way]))
            if temp_product > product:
                global move_way
                product = temp_product
                move_way = way
        print('move:', move_way)
        stage += 1
    elif stage == 2:
        move_dir = _unit_vector(player_p, first_arri)
        dist = math.hypot(player_p[0]-first_arri[0], player_p[1]-first_arri[1])
        dist_ball = math.hypot(player_p[0]-ball_p[0], player_p[1]-ball_p[1])
        print('arri-player-dist', first_arri, player_p, dist)
        if dist >= ERROR_DISTANCE and dist_ball > SAFE_DIST+8:
            direction = _rotate(player_d, WAY_ANGLE[move_way])
            angle = _angle(move_dir, direction)
            if angle > 0 and angle > 2*ROTATE_ANGLE:
                return ['Q1', 'N1', 'N1']
            elif angle < 0 and angle < -2*ROTATE_ANGLE:
                return ['E1', 'N1', 'N1']
            elif angle > 0 and angle > ROTATE_ANGLE:
                return ['q1', 'N1', 'N1']
            elif angle < 0 and angle < -ROTATE_ANGLE:
                return ['e1', 'N1', 'N1']
            '''
            MOVE
            '''
            if dist >= MOVE[move_way]['Bound'][0]:
                return [MOVE[move_way]['Fast'], 'N1', 'N1']
            elif dist >= MOVE[move_way]['Bound'][1]:
                return [MOVE[move_way]['Norm'], 'N1', 'N1']
        print('dist, dist_b:', int(dist), int(dist_ball))
        print('arri-player-dist', first_arri, player_p)
        print('========================================')
        stage += 1
    elif stage == 3:
        # Choose the way of kick
        if kick_way == "":
            print('S3 arri-player-dist', first_arri, player_p)
            product = -1
            for way in ALLOW_MOVE_WAY:
                temp_product = _dot(kick_dir, _rotate(player_d, WAY_ANGLE[way]))
                print(way, ':', temp_product, kick_dir, _rotate(player_d, WAY_ANGLE[way]))
                if temp_product > product:
                    product = temp_product
                    kick_way = way
            print("kick way", kick_way)
        dist_ball = math.hypot(player_p[0]-ball_p[0], player_p[1]-ball_p[1])
        dirction = _rotate(player_d, WAY_ANGLE[kick_way])
        angle = _angle(kick_dir, dirction)
        print('dist_b:', dist_ball)
        print('ang:', angle*180/math.pi)
        if angle > 0 and angle > 2*ROTATE_ANGLE:
            print('turn big left')
            return ['Q1', 'N1', 'N1']
        elif angle < 0 and angle < -2*ROTATE_ANGLE:
            print('turn big  right')
            return ['E1', 'N1', 'N1']
        elif angle > 0 and angle > ROTATE_ANGLE:
            print('turn left')
            return ['q1', 'N1', 'N1']
        elif angle < 0 and angle < -ROTATE_ANGLE:
            print('turn right')
            return ['e1', 'N1', 'N1']
        WAYS = ['F', 'R', 'B', 'L']
        for i in [1, 2, 3, 0]:
            move_way = WAYS[(WAYS.index(kick_way)+i) % 4]
            temp_dir = _rotate(dirction, math.pi/2*i)
            diff_vec = [k - p for k, p in zip(kick_point, player_p)]
            product = _dot(temp_dir, diff_vec)
            print(move_way, ':', product)
            if product > MOVE[move_way]['Bound'][1]:
                print('move:', MOVE[move_way]['Norm'])
                return [MOVE[move_way]['Norm'], 'N1', 'N1']
        stage += 1
    dist_ball = math.hypot(player_p[0]-ball_p[0], player_p[1]-ball_p[1])
    print('player, kick ball', player_p, kick_point, dist_ball)
    if kick_flag and not(kicked):
        print('===kicked===', MOVE[kick_way]['Kick'])
        sleep(1)  # For check
        return [MOVE[kick_way]['Kick'], 'N1', 'N1']
    return ['N1', 'N1', 'N1']
  

def get_sent_cmd(sentcmd, update):
    """
    Description:
        Simulator will pass the received strategy and a sending state
    Parameter:
        param1: list[str] -> received command
        param2: bool -> sent or not
    """
    # Your code
    if update:
        print('sent: ', sentcmd[0][0])
        if sentcmd[0][0] == 'N' and stage == 4:
            print('===N recieved==')
            global kick_flag
            kick_flag = True
        if sentcmd[0][0] == 'j' or sentcmd[0][0] == 'h':
            global kicked
            kicked = True
    pass


def _unit_vector(start, end):
    vector = [e - s for s, e in zip(start, end)]
    length = math.hypot(vector[0], vector[1])
    uniVector = [comp/length for comp in vector]
    return uniVector


def _dot(x, y):
    """Dot product as sum of list comprehension doing element-wise multiplication"""
    return sum(x_i*y_i for x_i, y_i in zip(x, y))


def _rotate(vector, angle):
    rot_vector = [0.0, 0.0]
    rot_vector[0] = (math.cos(angle)*vector[0]) - (math.sin(angle)*vector[1])
    rot_vector[1] = (math.sin(angle)*vector[0]) + (math.cos(angle)*vector[1])
    return rot_vector


def _angle(a, b):
    cross = a[0]*b[1] - a[1]*b[0]
    return math.asin(cross)


if __name__ == '__main__':
    Update_Robo_Info()