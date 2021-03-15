import cv2
import math
import time
import enum
import numpy as np

from simulator_appearance import *
import Strategy.challenge_3 as st_A
import Strategy.blank_strategy as st_B

# Virtual field parameter
#   Frame width is not field width, it is the size of simulation window
#   The size of the field is defined in BOUNDARY. You can use SCALE to adjust field size 
BOUNDARY = [(140, 70), (870, 70), (870, 170), (900, 170), (900, 350), (870, 350), (870, 450), (140, 450), (140, 350), (110, 350), (110, 170), (140, 170)]
CENTER = [0, 0]
FRAME_WIDTH, FRAME_HEIGHT = 1920/2, 1280/2
OFFSET = [0, 0] #Offset is to calibrate the total field position
SCALE = 1

# Game parameter
Side = 1 #1:Left A  Right B  #-1:Left B  Right A
CMD_FPS = 2
CAM_FPS = 15

# Robot movement parameter
Robo_rotate_speed = 0.025 #radius
'''
    the step size of a robot for each command
    [fast_for, for, back, move_left, move_right, fast_move_l, fast_move_r]
'''
Robo_move = [4, 3, 3, 4, 4, 6, 6]

# Ball simulation parameter
Ball_bump_speed = 3         # Bump speed when robot walking
Ball_kicked_speed = 4       # Robot kick speed
Ball_n_acce = 0.2           # Ball moving deacceleration
Ball_passing_speed = 2      # Robot pass speed
Ball_rotbump_speed = 4      # Bump speed when robot turning

# Simulator debug option
Cursor_Position_Show = 0

# Simulator inner parameter
Ball_direction = [1.0, 0.0]
Ball_Position = [0, 0]
Ball_speed = 0
FRAME_FPS = 30
Kickable_distance = 70
mode = 1 # ['start', 'pause', 'set']
Mouse_Position = [0, 0]
Robo_command = ['N1', 'N1', 'N1', 'N1', 'N1', 'N1']
Robo_Direction = [[1.0, 0.0], [1.0, 0.0], [1.0, 0.0], [-1.0, 0.0], [-1.0, 0.0], [-1.0, 0.0]]
Robo_kick_angle_threshold = 60*math.pi/180
Robo_Position = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]
Robo_rotate_rect = [None, None, None, None, None, None]
Robo_rotate_vert = [None, None, None, None, None, None]
Setup_Index = 0

# The simulation of object is simulated with update frequency @FRAME_FPS
# In practice, the camera has maximum update frequency of 30 fps. You can set this parameter with @CAM_FPS
# Also, the sending frequency in practice will not be 30 fps because it is too frequent for robot to reacat.
# YOu can modify the sending frequency in @CMD_FPS
# If you modify the value, you should modify object speed with appropriate scalar. Implement by yourself.
STRATEGY_UP, SEND_UP = int(FRAME_FPS/CAM_FPS), int(FRAME_FPS/CMD_FPS)

class MOVE(enum.Enum):
    NONE = 'N'
    FORWARD = 'w'
    BACKWARD = 's'
    TRUN_LEFT = 'q'
    TRUN_RIGHT = 'e'
    MOVE_LEFT = 'a'
    MOVE_RIGHT = 'd'
    F_FORWARD = 'W'
    F_MOVE_LEFT = 'A'
    F_MOVE_RIGHT = 'D'
    F_TRUN_LEFT = 'Q'
    F_TRUN_RIGHT = 'E'
    RFSHOOT = 'i'
    LFSHOOT = 'u'
    RSSHOOT = 'j'
    LSSHOOT = 'h'
    RBSHOOT = 'n'
    LBSHOOT = 'b'
    RPASS = 'p'
    LPASS = 'o'
    F_DEFENSE = 'Y'
    L_DEFENSE = 'f'
    R_DEFENSE = 'g'
    DEFENSE = 'y' 
    REST = 'r' 
    STAND = 'R'   
    STOP = 'x'  
    START = 'z'
    PK_MODE = 'c'

############################# Simulator Function ##################################
def field_reset(Robo_start_x, Robo_start_y, Keeper_start_x):
    """Field Initialize"""
    global Ball_Position,  Ball_speed, Robo_Direction, Robo_Position
    #Setup robot starting position
    Robo_Position[0][0] = int(CENTER[0] - Robo_start_x)
    Robo_Position[0][1] = int(CENTER[1] + Robo_start_y)
    Robo_Position[1][0] = int(CENTER[0] - Keeper_start_x)
    Robo_Position[1][1] = int(CENTER[1])
    Robo_Position[2][0] = int(CENTER[0] - Robo_start_x)
    Robo_Position[2][1] = int(CENTER[1] - Robo_start_y)
    Robo_Position[3][0] = int(CENTER[0] + Robo_start_x)
    Robo_Position[3][1] = int(CENTER[1] + Robo_start_y)
    Robo_Position[4][0] = int(CENTER[0] + Keeper_start_x)
    Robo_Position[4][1] = int(CENTER[1])
    Robo_Position[5][0] = int(CENTER[0] + Robo_start_x)
    Robo_Position[5][1] = int(CENTER[1] - Robo_start_y)
    #Setup robot starting direction
    Robo_Direction = [[1.0, 0.0], [1.0, 0.0], [1.0, 0.0], [-1.0, 0.0], [-1.0, 0.0], [-1.0, 0.0]]
    #Setup ball starting position
    Ball_Position = [int(CENTER[0]), int(CENTER[1])]
    Ball_speed = 0

def draw_empty(frame,FB_x, FB_y, PK_x, Penalty_y, Center_Circle, GA_x, GA_y):
    """Draw empty field"""
    #mark center
    cv2.rectangle(frame, (int(CENTER[0])-CenterHalfSize, int(CENTER[1])-CenterHalfSize), (int(CENTER[0])+CenterHalfSize, int(CENTER[1])+CenterHalfSize), Line_Color, -1)
    #mark middle line
    cv2.line(frame, (CENTER[0], BOUNDARY[0][1]), (CENTER[0], BOUNDARY[7][1]), Line_Color, 3)
    #mark goal line
    cv2.line(frame, (BOUNDARY[8][0],BOUNDARY[8][1]),(BOUNDARY[11][0],BOUNDARY[11][1]), Line_Color,3)
    cv2.line(frame, (BOUNDARY[2][0],BOUNDARY[2][1]),(BOUNDARY[5][0],BOUNDARY[5][1]), Line_Color,3)
    #Build FK FB PK point
    cv2.circle(frame, (int(CENTER[0]+FB_x), (int(CENTER[1]))), 5, Line_Color, -1, 8, 0)
    cv2.circle(frame, (int(CENTER[0]+FB_x), (int(CENTER[1]+FB_y))), 3, Line_Color, -1, 8, 0)
    cv2.circle(frame, (int(CENTER[0]+FB_x), (int(CENTER[1]-FB_y))), 3, Line_Color, -1, 8, 0)
    cv2.circle(frame, (int(CENTER[0]-FB_x), (int(CENTER[1]))), 5, Line_Color, -1, 8, 0)
    cv2.circle(frame, (int(CENTER[0]-FB_x), (int(CENTER[1]+FB_y))), 3, Line_Color, -1, 8, 0)
    cv2.circle(frame, (int(CENTER[0]-FB_x), (int(CENTER[1]-FB_y))), 3, Line_Color, -1, 8, 0)
    cv2.circle(frame, (int(CENTER[0]+PK_x), (int(CENTER[1]))), 5, Line_Color, -1, 8, 0)
    cv2.circle(frame, (int(CENTER[0]-PK_x), (int(CENTER[1]))), 5, Line_Color, -1, 8, 0)
    #Build Penalty Area
    cv2.line(frame,(int(CENTER[0]+PK_x),(int(CENTER[1]+Penalty_y))),(int(CENTER[0]+PK_x),(int(CENTER[1]-Penalty_y))), Line_Color,3)
    cv2.line(frame,(int(CENTER[0]-PK_x),(int(CENTER[1]+Penalty_y))),(int(CENTER[0]-PK_x),(int(CENTER[1]-Penalty_y))), Line_Color,3)
    cv2.line(frame,(int(CENTER[0]+PK_x),(int(CENTER[1]+Penalty_y))),(BOUNDARY[5][0],(int(CENTER[1]+Penalty_y))), Line_Color,3)
    cv2.line(frame,(int(CENTER[0]+PK_x),(int(CENTER[1]-Penalty_y))),(BOUNDARY[2][0],(int(CENTER[1]-Penalty_y))), Line_Color,3)
    cv2.line(frame,(int(CENTER[0]-PK_x),(int(CENTER[1]+Penalty_y))),(BOUNDARY[11][0],(int(CENTER[1]+Penalty_y))), Line_Color,3)
    cv2.line(frame,(int(CENTER[0]-PK_x),(int(CENTER[1]-Penalty_y))),(BOUNDARY[8][0],(int(CENTER[1]-Penalty_y))), Line_Color,3)
    #Build Goal Area
    cv2.line(frame,(int(CENTER[0]+GA_x),(int(CENTER[1]+GA_y))),(int(CENTER[0]+GA_x),(int(CENTER[1]-GA_y))), Line_Color,3)
    cv2.line(frame,(int(CENTER[0]-GA_x),(int(CENTER[1]+GA_y))),(int(CENTER[0]-GA_x),(int(CENTER[1]-GA_y))), Line_Color,3)
    cv2.line(frame,(int(CENTER[0]+GA_x),(int(CENTER[1]+GA_y))),(BOUNDARY[5][0],(int(CENTER[1]+GA_y))), Line_Color,3)
    cv2.line(frame,(int(CENTER[0]+GA_x),(int(CENTER[1]-GA_y))),(BOUNDARY[2][0],(int(CENTER[1]-GA_y))), Line_Color,3)
    cv2.line(frame,(int(CENTER[0]-GA_x),(int(CENTER[1]+GA_y))),(BOUNDARY[11][0],(int(CENTER[1]+GA_y))), Line_Color,3)
    cv2.line(frame,(int(CENTER[0]-GA_x),(int(CENTER[1]-GA_y))),(BOUNDARY[8][0],(int(CENTER[1]-GA_y))), Line_Color,3)
    #Center Circle
    cv2.circle(frame,(int(CENTER[0]),(int(CENTER[1]))),int(Center_Circle),Line_Color ,3, 8,0)
    #Draw Boundary
    cv2.line(frame, BOUNDARY[0],BOUNDARY[1], (0, 0, 255),5)
    cv2.line(frame, BOUNDARY[1],BOUNDARY[2], (0, 0, 255),5)
    cv2.line(frame, BOUNDARY[2],BOUNDARY[3], (0, 0, 255),5)
    cv2.line(frame, BOUNDARY[3],BOUNDARY[4], (0, 0, 255),5)
    cv2.line(frame, BOUNDARY[4],BOUNDARY[5], (0, 0, 255),5)
    cv2.line(frame, BOUNDARY[5],BOUNDARY[6], (0, 0, 255),5)
    cv2.line(frame, BOUNDARY[6],BOUNDARY[7], (0, 0, 255),5)
    cv2.line(frame, BOUNDARY[7],BOUNDARY[8], (0, 0, 255),5)
    cv2.line(frame, BOUNDARY[8],BOUNDARY[9], (0, 0, 255),5)
    cv2.line(frame, BOUNDARY[9],BOUNDARY[10], (0, 0, 255),5)
    cv2.line(frame, BOUNDARY[10],BOUNDARY[11], (0, 0, 255),5)
    cv2.line(frame, BOUNDARY[11],BOUNDARY[0], (0, 0, 255),5)

def draw_object(frame,FB_x, FB_y, PK_x, Penalty_y, Center_Circle, GA_x, GA_y):
    """Draw robot, ball and other info"""
     ##########################################################
    # Draw runtime image,like moving locus or moving target  #
    # Since color of runtime image may affect boundary judge #
    # of moving object, they cannot be placed 'in front of'  #
    # field's object (ex, boundary should never hoverd by    #
    # colors other than red), so we should draw them first.  #
    ##########################################################
    #Draw other information for debug. Ignore this block when you are not using strategy1 and 2
    try:
        pass
        frame = st_A.draw_on_simulator(frame)
        #frame = st_B.draw_on_simulator(frame)
    except AttributeError:
        pass

    #mark mouse marker
    cv2.rectangle(frame, (Mouse_Position[0], Mouse_Position[1]), (Mouse_Position[0]+MarkerSize, Mouse_Position[1]+MarkerSize), (255, 255, 255), -1)
    #mark mode text
    txt = ''
    if mode == 2:
        txt= mode_txt[mode]+str(Setup_Index)
    else:
        txt = mode_txt[mode]
    cv2.putText(frame, txt, (0, int(CENTER[1])), cv2.FONT_HERSHEY_SIMPLEX,1, TXT_Color, 5, cv2.LINE_AA)
    #mark Robot name
    cv2.putText(frame, Robo_name[0], (Robo_Position[0][0], Robo_Position[0][1]), cv2.FONT_HERSHEY_SIMPLEX,1, (102, 102, 0), 2, cv2.LINE_AA)
    cv2.putText(frame, Robo_name[1], (Robo_Position[1][0], Robo_Position[1][1]), cv2.FONT_HERSHEY_SIMPLEX,1, (102, 102, 0), 2, cv2.LINE_AA)
    cv2.putText(frame, Robo_name[2], (Robo_Position[2][0], Robo_Position[2][1]), cv2.FONT_HERSHEY_SIMPLEX,1, (102, 102, 0), 2, cv2.LINE_AA)
    cv2.putText(frame, Robo_name[3], (Robo_Position[3][0], Robo_Position[3][1]), cv2.FONT_HERSHEY_SIMPLEX,1, (102, 102, 0), 2, cv2.LINE_AA)
    cv2.putText(frame, Robo_name[4], (Robo_Position[4][0], Robo_Position[4][1]), cv2.FONT_HERSHEY_SIMPLEX,1, (102, 102, 0), 2, cv2.LINE_AA)
    cv2.putText(frame, Robo_name[5], (Robo_Position[5][0], Robo_Position[5][1]), cv2.FONT_HERSHEY_SIMPLEX,1, (102, 102, 0), 2, cv2.LINE_AA)  
    #Draw the Robot with rotate angle
    RoboColor = [TeamA_Color, TeamB_Color, TeamC_Color, OppoA_Color, OppoB_Color, OppoC_Color]
    for RoboIndex in range(len(Robo_Position)):
        angle = 0
        cross,dot,robo_angle,err = vector_product(Robo_Direction[RoboIndex][0], Robo_Direction[RoboIndex][1], 1, 0, 1)
        angle = 180 if err == 1 else robo_angle /math.pi * 180
        angle = -1 * angle if cross >= 0 else angle
        rot_rect = ((Robo_Position[RoboIndex][0], Robo_Position[RoboIndex][1]), (RoboDepth, RoboWidth), angle)
        box = cv2.boxPoints(rot_rect)
        box = np.int0(box)
        cv2.drawContours(frame,[box],0,RoboColor[RoboIndex],-1)
        global Robo_rotate_rect, Robo_rotate_vert
        Robo_rotate_vert[RoboIndex] = box
        Robo_rotate_rect[RoboIndex] = rot_rect
    #mark Team_Robot direction
    cv2.line(frame, (Robo_Position[0][0], Robo_Position[0][1]), (int(Robo_Position[0][0]+Robo_direction_length*Robo_Direction[0][0]), int(Robo_Position[0][1]+Robo_direction_length*Robo_Direction[0][1])), Robo_direction_Color,3)
    cv2.line(frame, (Robo_Position[1][0], Robo_Position[1][1]), (int(Robo_Position[1][0]+Robo_direction_length*Robo_Direction[1][0]), int(Robo_Position[1][1]+Robo_direction_length*Robo_Direction[1][1])), Robo_direction_Color,3)
    cv2.line(frame, (Robo_Position[2][0], Robo_Position[2][1]), (int(Robo_Position[2][0]+Robo_direction_length*Robo_Direction[2][0]), int(Robo_Position[2][1]+Robo_direction_length*Robo_Direction[2][1])), Robo_direction_Color,3)
    #mark Oppo_Robot direction
    cv2.line(frame, (Robo_Position[3][0], Robo_Position[3][1]), (int(Robo_Position[3][0]+Robo_direction_length*Robo_Direction[3][0]), int(Robo_Position[3][1]+Robo_direction_length*Robo_Direction[3][1])), Robo_direction_Color,3)
    cv2.line(frame, (Robo_Position[4][0], Robo_Position[4][1]), (int(Robo_Position[4][0]+Robo_direction_length*Robo_Direction[4][0]), int(Robo_Position[4][1]+Robo_direction_length*Robo_Direction[4][1])), Robo_direction_Color,3)
    cv2.line(frame, (Robo_Position[5][0], Robo_Position[5][1]), (int(Robo_Position[5][0]+Robo_direction_length*Robo_Direction[5][0]), int(Robo_Position[5][1]+Robo_direction_length*Robo_Direction[5][1])), Robo_direction_Color,3)    
    #mark ball
    cv2.circle(frame,(Ball_Position[0],Ball_Position[1]),BallHalfSize,Ball_Color,-1, 8,0)
    
    # cv2.circle(frame, (round(st_A.target[0]), round(st_A.target[1])), 2, (153,255,204), -1, 8, 0)

def CV_event(event, x, y, flags, param):
    """Mouse-event callback function"""
    global Robo_Position, Robo_Direction, Ball_Position, Ball_speed
    if event == cv2.EVENT_MOUSEMOVE and Cursor_Position_Show:#mouse move event
        print('Cousor position X: ',x,' Y: ',y,' Pixel BGR value: ',frame[y][x])  
    if event == cv2.EVENT_LBUTTONDOWN:# mouse left click event
        if mode == 2 and flags == cv2.EVENT_FLAG_LBUTTON:#Modify Robo position
            Robo_Position[Setup_Index] = [x,y].copy()
        elif mode == 2 and flags == cv2.EVENT_FLAG_SHIFTKEY + cv2.EVENT_FLAG_LBUTTON : #Press L Button and Press shift to change Robo direction         
            d_x = x - Robo_Position[Setup_Index][0]
            d_y = y - Robo_Position[Setup_Index][1]
            try:
                x_comp = d_x/math.hypot(d_x,d_y)
                y_comp = d_y/math.hypot(d_x,d_y)
                Robo_Direction[Setup_Index] = [x_comp,y_comp]
            except ZeroDivisionError:
                return
        else:
            #change mouse mark coordinate
            global Mouse_Position
            #Robo_Position[Setup_Index] = [x,y].copy()
            Mouse_Position = [x,y]
            print('Modify mouse position X: ',x,' Y: ',y,' Pixel BGR value: ',frame[y][x])
    if event == cv2.EVENT_RBUTTONDOWN:#mouse right click event
        Ball_speed = 0
        Ball_Position = [x,y]
        st_A.Update_Robo_Info(Robo_Direction[0:3], Robo_Position[0:3], Robo_Position[3:6], Ball_Position, Ball_speed, [0,0])
        st_B.Update_Robo_Info(Robo_Direction[3:6], Robo_Position[3:6], Robo_Position[0:3], Ball_Position)
        print('Modify Ball position X: ',x,' Y: ',y,' Pixel BGR value: ',frame[y][x]) 

def allmovement():
    """Tell all the robot for it's command"""
    for RoboIndex, command in enumerate(Robo_command):
        robomovement(RoboIndex, command[0])
    pass

'''
Move the robot in the simulator
We give a command to the robot, and the robot need to react to it as in the real world,
for this function, we give the robot id and the command give to the robot, then it judge the legitimacy of the move, 
if the move is legal, move it, if not, step one step back, and blink 
@param RoboIndex    =>  the ID of the robot to control
@param command      =>  the command for the robot
'''
def robomovement(RoboIndex, command):
    #Decide direction
    global Robo_Position, Robo_Direction, Ball_speed, Ball_direction # get excess to the robot position, direction, ballspeed and direction is for accidentily touching the ball

    # Total: 7
    if command == MOVE.FORWARD.value or command == MOVE.BACKWARD.value or \
        command == MOVE.MOVE_LEFT.value or command == MOVE.MOVE_RIGHT.value or \
            command == MOVE.F_FORWARD.value or command == MOVE.F_MOVE_LEFT.value or \
                command == MOVE.F_MOVE_RIGHT.value:
        robo_walk(RoboIndex, command)
        pass

    # Total: 4
    elif command == MOVE.TRUN_LEFT.value or command == MOVE.TRUN_RIGHT.value or \
        command == MOVE.F_TRUN_LEFT.value or command == MOVE.F_TRUN_RIGHT.value:
        robo_turn(RoboIndex, command)
        pass
    
    # Total: 2
    elif command == MOVE.RFSHOOT.value or command == MOVE.LFSHOOT.value:
        robo_shoot(RoboIndex, 0)
        pass

    # Total: 2
    elif command == MOVE.RSSHOOT.value or command == MOVE.LSSHOOT.value :
        robo_shoot(RoboIndex, 1)
        pass

    # Total: 2
    elif command == MOVE.RBSHOOT.value or command == MOVE.LBSHOOT.value:
        robo_shoot(RoboIndex, 2)
        pass

    # Total: 2
    elif command == MOVE.LPASS.value or command == MOVE.RPASS.value:
        robo_pass(RoboIndex)
        pass

    # Total: 5
    elif command == MOVE.NONE.value or command == MOVE.DEFENSE.value or \
        command == MOVE.STAND.value or command == MOVE.STOP.value or \
            command == MOVE.REST.value  or command == MOVE.START.value  or \
                command == MOVE.PK_MODE.value:
        pass

    # Total: 3
    elif command == MOVE.F_DEFENSE.value or command == MOVE.L_DEFENSE.value or \
        command == MOVE.R_DEFENSE.value:
        pass
    else:
        print("False command, error")

def robo_walk(RoboIndex, command):
    """Move one step"""
    #Decide direction
    global Robo_Position, Robo_Direction, Ball_speed, Ball_direction

    d_robo_x,d_robo_y = 0,0

    distance, unit_x, unit_y = 0, 0, 0
    

    # print(MOVE("N").values[1])
    if command == MOVE.F_FORWARD.value:
        distance = Robo_move[0]
        unit_x = Robo_Direction[RoboIndex][0]
        unit_y = Robo_Direction[RoboIndex][1]
    elif command == MOVE.FORWARD.value:
        distance = Robo_move[1]
        unit_x = Robo_Direction[RoboIndex][0]
        unit_y = Robo_Direction[RoboIndex][1]
    elif command == MOVE.BACKWARD.value:        # x=0*x+1*y, y=-1*x+0*y
        distance = Robo_move[2]
        unit_x = -Robo_Direction[RoboIndex][0]
        unit_y = -Robo_Direction[RoboIndex][1]
    elif command == MOVE.MOVE_LEFT.value:         # x=0*x-1*y, y=1*x+0*y
        distance = Robo_move[3]
        unit_x = Robo_Direction[RoboIndex][1]
        unit_y = -Robo_Direction[RoboIndex][0]
    elif command == MOVE.MOVE_RIGHT.value:        # x=0*x+1*y, y=-1*x+0*y
        distance = Robo_move[4]
        unit_x = -Robo_Direction[RoboIndex][1]
        unit_y = Robo_Direction[RoboIndex][0]
    elif command == MOVE.F_MOVE_LEFT.value:         # x=0*x-1*y, y=1*x+0*y
        distance = Robo_move[5]
        unit_x = Robo_Direction[RoboIndex][1]
        unit_y = -Robo_Direction[RoboIndex][0]
    elif command == MOVE.F_MOVE_RIGHT.value:        # x=0*x+1*y, y=-1*x+0*y
        distance = Robo_move[6]
        unit_x = -Robo_Direction[RoboIndex][1]
        unit_y = Robo_Direction[RoboIndex][0]
    else:
        pass

    for i in range(0,round(distance),1):   
        d_robo_x = d_robo_x + unit_x
        d_robo_y = d_robo_y + unit_y
        #When moving, check if bump into other robot or boundary or ball
        bump_boundary = 0
        #Calculate new rectangle of next move (in OpenCV, rotated rectangle angle is in degree not radius)
        tmp_angle = 0
        tmp_cross, tmp_dot, robo_angle, tmp_err = vector_product(Robo_Direction[RoboIndex][0], Robo_Direction[RoboIndex][1], 1, 0, 1)
        tmp_angle = 180 if tmp_err == 1 else robo_angle /math.pi * 180
        tmp_angle = -1 * tmp_angle if tmp_cross >= 0 else tmp_angle
        tmp_rot_rect = ((Robo_Position[RoboIndex][0]+round(d_robo_x), Robo_Position[RoboIndex][1]+round(d_robo_y)), (RoboDepth, RoboWidth), tmp_angle)
        #Parse this new rectangle to bump detection
        bump_boundary,__ = robo_bump(RoboIndex, tmp_rot_rect)
        #If bump with ball then ball moving
        if bump_boundary == 3:
            Ball_speed = 3*Ball_bump_speed
            Ball_direction = [unit_x, unit_y]
        #Below should be the final case since it might break the loop
        #If robot do bump something
        if bump_boundary != 0 :
            # d_robo_x = d_robo_x - unit_x
            # d_robo_y = d_robo_y - unit_y
            d_robo_x = 0
            d_robo_y = 0
            break
        
        
    #Robo_Direction[RoboIndex] = [unit_x, unit_y]
    Robo_Position[RoboIndex][0] = Robo_Position[RoboIndex][0] + round(d_robo_x)
    Robo_Position[RoboIndex][1] = Robo_Position[RoboIndex][1] + round(d_robo_y)

def robo_turn(RoboIndex, command):#direction 1:counterclockwise  0:clockwise
    """Turn Robo one time"""
    global Robo_Direction, Ball_speed, Ball_direction
    x_dir = Robo_Direction[RoboIndex][0]
    y_dir = Robo_Direction[RoboIndex][1]

    rotate_angle = 0
    if command == MOVE.TRUN_RIGHT.value:
        rotate_angle = Robo_rotate_speed
    elif command == MOVE.TRUN_LEFT.value:
        rotate_angle = -1 * Robo_rotate_speed
    elif command == MOVE.F_TRUN_RIGHT.value:
        rotate_angle = Robo_rotate_speed*2
    elif command == MOVE.F_TRUN_LEFT.value:
        rotate_angle = -2 * Robo_rotate_speed
    # rotate_angle = Robo_rotate_speed if command == MOVE.TRUN_RIGHT.value else -1 * Robo_rotate_speed
    rotate_cos = math.cos(rotate_angle)
    rotate_sin = math.sin(rotate_angle)
    x_final, y_final = x_dir*rotate_cos - y_dir*rotate_sin, x_dir*rotate_sin + y_dir*rotate_cos
    
    #Collision might happen when rotate. Just as what we do in Robo moving, Calculate new rectangle of next move first.
    tmp_angle = 0
    tmp_cross, tmp_dot, robo_angle, tmp_err = vector_product(x_final, y_final, 1, 0, 1)
    tmp_angle = 180 if tmp_err == 1 else robo_angle /math.pi * 180
    tmp_angle = -1 * tmp_angle if tmp_cross >= 0 else tmp_angle
    tmp_rot_rect = ((Robo_Position[RoboIndex][0], Robo_Position[RoboIndex][1]), (RoboDepth, RoboWidth), tmp_angle)
    #Parse this new rectangle to bump detection
    bump_boundary,rot_bump_position = robo_bump(RoboIndex, tmp_rot_rect)
    if bump_boundary == 3:
        Ball_speed = Ball_rotbump_speed
        ball_dir_x = Ball_Position[0] - rot_bump_position[0]
        ball_dir_y = Ball_Position[1] - rot_bump_position[1]
        length = math.hypot(ball_dir_x, ball_dir_y)
        ball_d_x = ball_dir_x/length
        ball_d_y = ball_dir_y/length
        Ball_direction = [ball_d_x, ball_d_y]
    elif bump_boundary == 0:
        Robo_Direction[RoboIndex] = [x_final, y_final]

def robo_bump(RoboIndex, rot_rect):
    """Detect bumping with Boundary, ball,Robot when robot is moving"""
    bump_boundary = 0
    rot_bump_position = [0, 0]
    vertices = cv2.boxPoints(rot_rect)
    vertices = np.int0(vertices).tolist()
    ###################################################################################
    # Detect Robot-Robot collision by OpenCV rotatedRectangleIntersection function    #
    # Return 1 if bump                                                                #
    ###################################################################################
    if bump_boundary == 0:
        for rec_index, rect in enumerate(Robo_rotate_rect):
            if rec_index == RoboIndex:
                pass
            else:
                intersect = cv2.rotatedRectangleIntersection(rect, rot_rect)
                if intersect[0] != 0:
                    bump_boundary = 1
                    print(RoboIndex,' bump with ',rec_index)
                    break
    ###################################################################################
    # Detect Robot-boundary collision by reading rectangle vertices' BGR value        #
    # Return 2 if bump                                                                #
    ###################################################################################
    if bump_boundary == 0:
        for vert_index, vert in enumerate(vertices):
            if (frame[vert[1]][vert[0]] == Boundary_Color).all():
                bump_boundary = 2
                break
    ###################################################################################
    # Detect Robot-ball collision by vector (use vector to calculate distance)        #
    # Return 3 if bump                                                                #
    # To calculate point P to line AB, consider vector AC,which is projection of      #
    # vector AP on Vector AB. AC has same direction as AB and its scale can be        #
    # obtained by [(AP*AB)/(AB*AB)]. If scale <1 then C is located between AB, length #
    # is equal to length of vector CP needless to say. If scale <=0 then length is    #
    # equal to length AP since AP has a opposite projection on AB. If scale >=1 then  #
    # length is equal to lengthBP clearly.                                            #
    ###################################################################################
    if bump_boundary == 0:
        for vert_index, vert in enumerate(vertices):
            line_pointA = [vert[0], vert[1]]
            end_index = 0 if vert_index == 3 else vert_index + 1
            line_pointB = [vertices[end_index][0], vertices[end_index][1]]
            vect_A_B = [line_pointB[0]-line_pointA[0], line_pointB[1]-line_pointA[1]]#Vector A2B
            vect_A_ball = [Ball_Position[0] - line_pointA[0], Ball_Position[1] - line_pointA[1]]#Vector A2Ball
            #Calculate the Projection of A2Ball on A2B i.e  (AdotB)/lengthAB^2 * vectorAB
            dot = vector_product(vect_A_ball[0],vect_A_ball[1],vect_A_B[0],vect_A_B[1],0)[1]
            ABlength_sqa = math.pow(math.hypot(vect_A_B[0], vect_A_B[1]),2)
            Projection_scale = dot/ABlength_sqa
            BallonEgde_x, BallonEgde_y = vect_A_B[0]*Projection_scale, vect_A_B[1]*Projection_scale
            vect_BallonEgde = [BallonEgde_x, BallonEgde_y]
            #Calculate ball to edge distance
            edge_ball_distance = 0
            if Projection_scale <= 0:
                rot_bump_position = line_pointA
                edge_ball_distance = math.hypot(vect_A_ball[0],vect_A_ball[1])
            elif Projection_scale >= 1:
                rot_bump_position = line_pointB
                vect_B_ball = [x1 - x2 for (x1, x2) in zip(vect_A_ball, vect_A_B)]
                edge_ball_distance = math.hypot(vect_B_ball[0], vect_B_ball[1])
            else:
                rot_bump_position = [x1 + x2 for (x1, x2) in zip(line_pointA, vect_BallonEgde)]
                vect_P_ball = [x1 - x2 for (x1, x2) in zip(vect_A_ball, vect_BallonEgde)]#Projection point to Ball
                edge_ball_distance = math.hypot(vect_P_ball[0], vect_P_ball[1])
            #Judge if bump with ball
            if edge_ball_distance <= 6:
                bump_boundary = 3
                print(RoboIndex,' bump ball --distance: ',edge_ball_distance)
                break
    return bump_boundary ,rot_bump_position #Second return only meaningful when bump_boundary == 3

def vector_product(p1_x, p1_y, p2_x, p2_y, unit_vector=0):
    """
    Description:
        CAlculate cross/dot product and angle of two given vector
    Parameters:
        p1, p2 are two endpoints
        unit_vector: set to 1 if given vectors are unit vector
    Return:
        cross product, dor product, angle, and error flag, 1 if there is error.
    """
    ValueErrorFlag = 0
    cro = p1_x * p2_y - p1_y * p2_x
    dot = p1_x * p2_x + p1_y * p2_y
    dot_angle = dot if unit_vector == 1 else dot/(math.hypot(p1_x,p1_y)*math.hypot(p2_x,p2_y))
    angle = 0
    try:
        angle = math.acos(dot_angle)
    except  ValueError:
        ValueErrorFlag = 1
        return cro,dot,0,ValueErrorFlag
    return cro,dot,angle,ValueErrorFlag

def robo_shoot(RoboIndex, cmd = 0):
    """Robot Shoot"""
    global Ball_speed, Ball_direction
    d_ball_x = Ball_Position[0]-Robo_Position[RoboIndex][0]
    d_ball_y = Ball_Position[1]-Robo_Position[RoboIndex][1]
    distance = math.hypot(d_ball_x, d_ball_y)
    unit_ball_x = d_ball_x/distance
    unit_ball_y = d_ball_y/distance
    cross,dot,ball_angle_dif,err = vector_product(Robo_Direction[RoboIndex][0], Robo_Direction[RoboIndex][1], unit_ball_x, unit_ball_y,1)
    ball_angle_dif = math.pi if err and dot <= -1 else ball_angle_dif
    if ball_angle_dif > Robo_kick_angle_threshold and cmd == 0:
        print(RoboIndex,' kick angle too large, miss')
        return
    elif (ball_angle_dif - 0.5 * math.pi) > Robo_kick_angle_threshold and cmd == 1:
        print(RoboIndex,' kick angle too large, miss')
        return
    elif (ball_angle_dif - 1 * math.pi) > Robo_kick_angle_threshold and cmd == 2:
        print(RoboIndex,' kick angle too large, miss')
        return
    else:
        #If ball is not too far
        if distance <= Kickable_distance:
            if cmd == 0:
                Ball_direction = [Robo_Direction[RoboIndex][0],Robo_Direction[RoboIndex][1]]
                Ball_speed = Ball_kicked_speed
            elif cmd == 1:
                Ball_direction = [unit_ball_x,unit_ball_y]
                Ball_speed = Ball_kicked_speed * 0.5
            elif cmd == 2:
                Ball_direction = [-Robo_Direction[RoboIndex][0],-Robo_Direction[RoboIndex][1]]
                Ball_speed = Ball_kicked_speed
            else:
                pass
            
            print('Robo ',RoboIndex,' Play a shoot')   
        else:
            print(RoboIndex,' too far, miss')
            return

def robo_pass(RoboIndex):
    """Robot Pass"""
    global Ball_speed, Ball_direction
    #Angle is correct then kick
    d_ball_x = Ball_Position[0]-Robo_Position[RoboIndex][0]
    d_ball_y = Ball_Position[1]-Robo_Position[RoboIndex][1]
    distance = math.hypot(d_ball_x, d_ball_y)
    unit_ball_x = d_ball_x/distance
    unit_ball_y = d_ball_y/distance
    cross,dot,ball_angle_dif,err = vector_product(Robo_Direction[RoboIndex][0], Robo_Direction[RoboIndex][1], unit_ball_x, unit_ball_y,1)
    ball_angle_dif = math.pi if err and dot <= -1 else ball_angle_dif
    if ball_angle_dif > Robo_kick_angle_threshold:
        print(RoboIndex,' PASS angle too large, miss')
        return
    else:
        #If ball is not too far
        if distance <= Kickable_distance:
            Ball_direction = [Robo_Direction[RoboIndex][0],Robo_Direction[RoboIndex][1]]
            Ball_speed = Ball_passing_speed
            print('Robo ',RoboIndex,' Play a PASS')   
        else:
            print(RoboIndex,'PASS too far, miss')
            return

def ball_move():
    """Simulation of ball"""
    global Ball_speed,Ball_direction
    try:
        d_ball_X, d_ball_Y = 0, 0
        Color = [Boundary_Color,TeamA_Color,TeamB_Color,TeamC_Color,OppoA_Color,OppoB_Color,OppoC_Color]
        for i in range(0,int(Ball_speed),1):
            bound_x, bound_y = 0, 0

            #Check if collision happen when moving to next position
            #X and Y are separated
            d_ball_X = d_ball_X + 1 * Ball_direction[0]
            size_offset = BallHalfSize if d_ball_X >= 0 else -1 * BallHalfSize
            for bound_color in Color:
                if (frame[ int(round(Ball_Position[1]+d_ball_Y+size_offset)) ][ int(round(Ball_Position[0]+d_ball_X+size_offset)) ] == bound_color).all() or\
                    (frame[ int(round(Ball_Position[1]+d_ball_Y-size_offset)) ][ int(round(Ball_Position[0]+d_ball_X+size_offset)) ] == bound_color).all():
                    bound_x = 1
                    break
            d_ball_X = d_ball_X - 1 * Ball_direction[0]

            d_ball_Y = d_ball_Y + 1 * Ball_direction[1]
            size_offset = BallHalfSize if d_ball_Y >= 0 else -1 * BallHalfSize
            for bound_color in Color:
                if (frame[ int(round(Ball_Position[1]+d_ball_Y+size_offset)) ][ int(round(Ball_Position[0]+d_ball_X+size_offset)) ] == bound_color).all() or\
                    (frame[ int(round(Ball_Position[1]+d_ball_Y+size_offset)) ][ int(round(Ball_Position[0]+d_ball_X-size_offset)) ] == bound_color).all():
                    bound_y = 1
                    break
            d_ball_Y = d_ball_Y - 1 * Ball_direction[1]
            
            d_ball_X = d_ball_X  if bound_x else d_ball_X + Ball_direction[0]
            d_ball_Y = d_ball_Y  if bound_y else d_ball_Y + Ball_direction[1]
            Ball_direction[0] = -1 * Ball_direction[0] if bound_x else Ball_direction[0]
            Ball_direction[1] = -1 * Ball_direction[1] if bound_y else Ball_direction[1]

    except ZeroDivisionError:
        d_ball_X, d_ball_Y= 0, 0
    finally:
        Ball_Position[0] = Ball_Position[0] + int(round(d_ball_X))
        Ball_Position[1] = Ball_Position[1] + int(round(d_ball_Y))
        Ball_speed = 0 if Ball_speed - Ball_n_acce < 0 else Ball_speed - Ball_n_acce

def get_strategy():
    """Simulator get strategy"""
    #try:
    cmd_a = st_A.strategy()
    cmd_b = st_B.strategy()
    #except AttributeError:
        #return 0,0,0
    return 1, cmd_a, cmd_b

def init_strategy():
    """Initialize strategy"""
    global Robo_Position, Robo_Direction
    try:
        st_A.Initialize()
        st_B.Initialize()
    except AttributeError:
        pass

def parse_strategy_field(PK_x, FB_x, FB_y, Penalty_y):
    """Parse field parameter to strategy"""
    try:
        (sideA, sideB) = (1, -1) if Side == 1 else (-1, 1)
        st_A.strategy_update_field(sideA, BOUNDARY, CENTER, PK_x, FB_x, FB_y, Penalty_y, GA_x, GA_y)
        st_B.strategy_update_field(sideB, BOUNDARY, CENTER, PK_x, FB_x, FB_y, Penalty_y, GA_x, GA_y)
    except AttributeError:
        pass

def return_sent_cmd(send_data, sent):
    """Pass sent command to strategy"""
    try:
        st_A.get_sent_cmd(send_data[0:3], sent)
        st_B.get_sent_cmd(send_data[3:6], sent)
    except AttributeError:
        pass

def upd_strategy_position():
    """Simulator Opject position update"""
    try:
        a_offset = 0
        b_offset = 0
        if Side == 1:
            a_offset = 0
            b_offset = 3
        else:
            a_offset = 3
            b_offset = 0
        st_A.Update_Robo_Info(Robo_Direction[a_offset:a_offset+3], Robo_Position[a_offset:a_offset+3], Robo_Position[b_offset:b_offset+3], Ball_Position, 0, [0, 0])
        st_B.Update_Robo_Info(Robo_Direction[b_offset:b_offset+3], Robo_Position[b_offset:b_offset+3], Robo_Position[a_offset:a_offset+3], Ball_Position)
    except AttributeError:
        pass


if __name__ == '__main__':

    # Calculate boundary coordinate with offset and mew CENTER
    for index,position in enumerate(BOUNDARY):
        BOUNDARY[index] = (int(position[0]*SCALE)+OFFSET[0],int(position[1]*SCALE)+OFFSET[1])
    center_x = (BOUNDARY[0][0] + BOUNDARY[1][0])/2
    center_y = (BOUNDARY[0][1] + BOUNDARY[7][1])/2
    CENTER = [int(center_x),int(center_y)]
    print('Virtual Field Center Position',CENTER)

    # Calculate field building parameter
    In_Field_Width = abs(BOUNDARY[0][0] - BOUNDARY[1][0])  
    In_Field_Height = abs(BOUNDARY[0][1] - BOUNDARY[7][1])
    FB_x           = int(In_Field_Width*80/340)
    FB_y           = int(In_Field_Height*40/180)
    PK_x           = int(In_Field_Width*110/340)
    Penalty_y      = int(In_Field_Height*65/180)
    Center_Circle  = int(In_Field_Height*30/180)
    Robo_start_x   = int(In_Field_Width*110/340)
    Robo_start_y   = int(In_Field_Height*40/180)
    Keeper_start_x = int(In_Field_Width*145/340)
    GA_x            = int(In_Field_Width*150/340)
    GA_y            = int(In_Field_Height*45/180)
    # Set objects position
    field_reset(Robo_start_x, Robo_start_y, Keeper_start_x)

    # Create window and register mouse/keyboard event
    cv2.namedWindow('frame')
    cv2.setMouseCallback('frame',CV_event)

    # Draw empty field
    empty_field = np.zeros((1080,1920,3), np.uint8)
    empty_field = cv2.resize(empty_field, ( int(FRAME_WIDTH) , int(FRAME_HEIGHT) ))
    draw_empty(empty_field,FB_x,FB_y,PK_x,Penalty_y,Center_Circle, GA_x, GA_y)
    
    #Parse field parameter to strategy and initialize strategy
    parse_strategy_field(PK_x, FB_x, FB_y, Penalty_y)
    init_strategy() 

    # Initialize cmd
    cmd_a, cmd_b = [None]*3, [None]*3

    start = 0 #start after enter 's'
    strategy_timer, send_timer = 0, 0
    
    while True:
        # Start timer
        tStart = time.time()

        # copy empty field and draw object
        frame = empty_field.copy()
        draw_object(frame,FB_x,FB_y,PK_x,Penalty_y,Center_Circle, GA_x, GA_y)

        #If ball is in the goal area then this match is finished.
        if Ball_Position[0] <= BOUNDARY[0][0] or Ball_Position[0] >= BOUNDARY[1][0]:
            start, mode = 0, 1
        if start:
        ###################################### strategy ##########################################
            if strategy_timer == 0:
                # Update strategy information first and then get strategy
                upd_strategy_position()
                # Get stategy
                success,cmd_atmp,cmd_btmp = get_strategy()
                (cmd_a, cmd_b) = (cmd_atmp, cmd_btmp) if success else (cmd_a, cmd_b)

            if send_timer == 0:
                # Send(simulate) command
                Robo_command[0:3] = cmd_a
                Robo_command[3:6] = cmd_b
                return_sent_cmd(Robo_command, True)
            else:
                return_sent_cmd([cmd_a, cmd_b], False)

            allmovement()
            ball_move()

            # Update timer
            strategy_timer = strategy_timer + 1 if strategy_timer < STRATEGY_UP-1 else 0
            send_timer = send_timer + 1 if send_timer < SEND_UP-1 else 0
        # Show the result of this loop
        cv2.imshow('frame', frame)
        ################################## Keyboard detector #####################################
        k = cv2.waitKey(1) & 0xFF
        if  k == ord('q'):# Quit
            break
        elif  k == ord('s'):# Start
            start, mode = 1, 0
        elif  k == ord('p'):# Pause
            start, mode = 0, 1
        elif  k == ord('r'):# Reset Simulation
            start, mode = 0, 1
            field_reset(Robo_start_x, Robo_start_y, Keeper_start_x)
            init_strategy()
        elif  k == ord('c'):# Open Cursor Tracker
            Cursor_Position_Show = not Cursor_Position_Show
            print('Cursor','On' if Cursor_Position_Show else 'OFF')
        elif  k == ord('k'):# Kick all robot outside the field
            start, mode = 0, 1
            for i in range(len(Robo_Position)):
                Robo_Position[i] = [0,0]
        elif  k == ord('o'): # Set robot position
            start, mode = 0, 2
        elif  mode == 2 and k <= ord('5') and k >= ord('0'):
            Setup_Index = k-ord('0') #Robo 0 to 5 index 0 to 5

        while time.time() - tStart < 1/FRAME_FPS:
            pass
    # Close all frames #
    cv2.destroyAllWindows()