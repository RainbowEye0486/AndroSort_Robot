import constant as CONST
from enum import Enum

# Parameter needed to adjust
ID_IN_USE = [3, 4]

# Field Parameter
BOUNDARY = []
CENTER = [0, 0]
PENALTY

#  
robots = []
enemies = []
ball = None


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
    global BOUNDARY, CENTER, PENALTY
    BOUNDARY = boundary
    CENTER = center
    PENALTY = penalty


def Initialize():
    """
    Description:
        Initialise the strategy.
        This function will be called by the simulator before a simulation is started.
    """
    global robots, enemies, ball
    for i in range(2):
        robots.append(Robot(ID_IN_USE[i]))
    # for i in range(2):
    #     enemies.append(Enemy())
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


def Update_Robo_Info(teamD, teamP, oppoP, ballP):
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
    # Your code
    for i in range(3):
        if len(teamP[i]) > 0:
            robots[i].pos = teamP[i]
        if len(teamD[i] > 0):
            robots[i].dir = teamD[i]
        if len(oppoP) >= i + 1:
            enemies[i] = oppoP[i]
    ball.pos = ballP
    # ball.sped = ballS
    # return False


def strategy(roboID):
    """
    Description:
        The simulator will ask for strategy after calling Update_Robo_Info()
    Return:
        retva1: str -> command for this robot
    """
    # Your code
    global robots
    # choose_mode() # as a defender or an atacker
    assign_role(robots, roboID)
    assign_job(robots, roboID)
    cmd = execute_job(robots, roboID)
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


def assign_role(robots, id):
    '''
    Decide every robot's role and change robot's attribute: role
    '''
    robots[0].role = 's'
    robots[1].role = ''


def assign_job(robots, id):
    '''
    Decide every robot's job and change robot's attribute: job
    '''
    if robots[0].job == '':
        robots[0].job = ''


def execute_job(robots, id):
    """
    Base on the robot's job, give an exact command
    """
    robot = robots[id]
    if robot.job == Job.MOVE:
        pass
    elif robot.job == Job.PASS:
        pass


class Robot():
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
        self.pos = [0, 0]
        self.dir = [0, 0]
        self.role = ''
        self.job = Job.NONE
        self.MOTION = CONST.getMotion(ID)
        self.BODY = CONST.getBody(ID)


class Role(Enum):
    NONE = 0
    MAIN = 1  # attacker or defender
    SUP = 2  # supporter
    GK = 3


class Job(Enum):
    NONE = 0
    MOVE = 1
    PASS = 2


class Enemy():
    def __init__(self):
        self.pos = [0, 0]


class Ball():
    def __init__(self):
        self.pos = [0, 0]
        self.RADIUS = CONST.getRadius()


if __name__ == '__main__':
    pass
