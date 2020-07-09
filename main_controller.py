import time
from threading import Thread
import cv2
from Vision import Image_Identifier as image
from Strategy import challenge_1 as strategy1  # change this
from Strategy import challenge_2 as strategy2  # change this
from Strategy import challenge_3 as strategy3  # change this
from Strategy import challenge_pk as strategy_pk  # change this
from comm import nrf_controller as nrf
from queue import Queue
import platform
import tkinter as tk
import sys


PRINT = True

if 'Linux' in platform.system():
    from getch import getch
elif 'Windows' in platform.system():
    from msvcrt import getwch as getch
else:
    from getch import getch

image_buffer = list()
decision_done = False
wait_flag = False
# 需要調整參數
# ===========adjust==========================
side = -1  # -1 for <- , 1 for -> (left is our field)
challenge_num = 1
PK = True
# ===========================================

crouch = [False, False, False]
go_strategy = False
rest_bit = False
start_bit = False
time_S = 0
time_E = 0
wait_initial = [0, 0]

if challenge_num == 1:
    strategy = strategy1
    image.challenge_bit = 1
if challenge_num == 2:
    strategy = strategy2
    image.challenge_bit = 2
if challenge_num == 3:
    strategy = strategy3
    image.challenge_bit = 3
if challenge_num == 4:
    strategy = strategy_pk
    image.challenge_bit = 0


def ready_func():
    global start_bit
    start_bit = True
    if challenge_num == 1:
        strategy.restart()


def start_func():
    global go_strategy, rest_bit, wait_flag, time_S
    go_strategy = True
    rest_bit = False
    time_S = time.time()


def pause_func():
    global go_strategy, wait_flag
    go_strategy = False
    wait_flag = False


def PK_func():
    global PK
    if PK:
        PK = False
        strategy3.PK_bit = False
    else:
        PK = True
        strategy3.PK_bit = True
    print(PK)


def side_func():
    global side
    if side == 1:
        side = -1
        strategy.SIDE = -1
        strategy.strategy_update_field(side, image.field_pos, image.middle, image.penalty_pos)
    else:
        side = 1
        strategy.SIDE = 1
        strategy.strategy_update_field(side, image.field_pos, image.middle, image.penalty_pos)


def def_wait():
    global wait_flag
    wait_flag = True


def expo_func(self):
    image.cap.stream.set(cv2.CAP_PROP_EXPOSURE, s2.get())


def exit_func():
    window.destroy()
    image.exit_bit = 1
    sys.exit(0)


def rest_func():
    global go_strategy, rest_bit, wait_flag
    go_strategy = False
    wait_flag = False
    rest_bit = True


def print_func():
    strategy.PRINT = not strategy.PRINT


def change_func():
    strategy.change_robots(from_string.get(), to_string.get())


def Image_thread():
    image.image_func()


def Strategy_thread(que):
    #  first set field coordinate
    global go_strategy, wait_flag
    record = False
    strategy.Initialize()
    strategy.strategy_update_field(side, image.field_pos, image.middle, image.penalty_pos)
    while True:
        """print("our direction", image.our_dir)
        print("our position", image.our_data)
        print("enemy position", image.enemy_data)
        print("ball position", image.ball_pos_now)"""
        # print("enemy position", image.enemy_data)
        global time_E, wait_initial
        if image.exit_bit != 0:
            sys.exit()
        if go_strategy:

            if challenge_num == 2:
                time.sleep(1.0)
            elif challenge_num == 1:
                time.sleep(0.5)
                #  修改 發送延遲時間
            elif challenge_num == 3:
                if strategy3.robots[2].job == strategy3.Job.DIVE:
                    time.sleep(0.05)
                else:
                    time.sleep(0.4)

            strategy.Update_Robo_Info(image.our_dir, image.our_data, image.enemy_data, image.ball_pos_now,
                                      image.ball_speed, image.ball_dir)
            # print('u_f in main b', image.update_frame)
            if challenge_num == 3:
                if wait_flag:
                    if not record:
                        wait_initial = strategy.ball.pos
                        record = True
                    time_E = time.time()
                    print((time_E - time_S), strategy.get_distance(wait_initial, strategy.ball.pos))
                    if (time_E - time_S) > 10 or strategy.get_distance(wait_initial,
                                                                       strategy.ball.pos) > 3 * strategy.CM_TO_PIX:
                        wait_flag = False
                        record = False
                        pass
                    else:
                        continue
            cmd = strategy.strategy()
            try:
                input_data = cmd
                if PRINT:
                    print('cmd:', input_data)
                if que.empty():
                    que.put(input_data)
                    time.sleep(0.001)
                else:
                    que.get()
                    que.put(input_data)
                    time.sleep(0.001)
            except OverflowError:
                print('invalid cmd value')
        else:  # clean the buffer when pause
            if not que.empty():
                que.get()
        time.sleep(0.01)


def NRF_thread(device, que):
    global crouch, start_bit, rest_bit, go_strategy
    while True:
        if image.exit_bit != 0:
            nrf.rest_robots(device)
            sys.exit()
        if start_bit:
            start_bit = False
            if que.empty():
                que.put(['z', 'z', 'z'])
                time.sleep(0.001)
            else:
                que.get()
                que.put(['z', 'z', 'z'])
                time.sleep(0.001)
        if rest_bit:
            rest_bit = False
            if que.empty():
                que.put(['x', 'x', 'x'])
                time.sleep(0.001)
            else:
                que.get()
                que.put(['x', 'x', 'x'])
                time.sleep(0.001)
        crouch = nrf.communicate(device, que, crouch)


if __name__ == '__main__':
    nrf.read_config()
    state, device, baud = nrf.device_chose()
    if state == 1:
        nrf.download_cfg(device)
        cmd_in_wait = Queue(5)
        thread1 = Thread(target=Image_thread, name='Im_Tr')
        thread1.start()
        time.sleep(0.5)
        image.return_field()
        thread2 = Thread(target=Strategy_thread, name='C2_Tr', args=(cmd_in_wait,))
        thread2.start()
        time.sleep(0.5)
        thread3 = Thread(target=NRF_thread, name='Comm_Tr', args=(device, cmd_in_wait,))
        thread3.start()
        time.sleep(0.5)

    # all the setting of button
    window = tk.Tk()

    s2 = tk.Scale(window, from_=30, to=180, orient="horizontal", command=expo_func, tickinterval=5, resolution=5)
    s2.pack()
    pick_color_frame = tk.Frame(window)
    pick_color_frame.pack()
    change_frame = tk.Frame(window)
    change_frame.pack()
    instruction_frame = tk.Frame(window)
    instruction_frame.pack(side=tk.BOTTOM)

    labelLand = tk.Label(change_frame,
                         text="From")
    labelLand.grid(column=0, row=0, sticky=tk.W)
    labelCity = tk.Label(change_frame,
                         text="To")
    labelCity.grid(column=0, row=1, sticky=tk.W)

    from_string = tk.StringVar()
    to_string = tk.StringVar()
    entryLand = tk.Entry(change_frame, width=20, textvariable=from_string)
    entryCity = tk.Entry(change_frame, width=20, textvariable=to_string)

    entryLand.grid(column=1, row=0, padx=10)
    entryCity.grid(column=1, row=1, padx=10)

    resultButton = tk.Button(change_frame, text='Get Result',
                             command=change_func)

    resultButton.grid(column=0, row=2, pady=10, sticky=tk.W)

    resultString = tk.StringVar()
    resultLabel = tk.Label(change_frame, textvariable=resultString)
    resultLabel.grid(column=1, row=2, padx=10, sticky=tk.W)

    our_button = tk.Button(pick_color_frame, text='our', fg='Red', command=image.set_our)
    our_button.pack(side=tk.LEFT)
    enemy_button = tk.Button(pick_color_frame, text='enemy', fg='Blue', command=image.set_enemy)
    enemy_button.pack(side=tk.LEFT)
    color1_button = tk.Button(pick_color_frame, text='color1', fg='Brown', command=image.set_color1)
    color1_button.pack(side=tk.LEFT)
    color2_button = tk.Button(pick_color_frame, text='color2', fg='Green', command=image.set_color2)
    color2_button.pack(side=tk.LEFT)
    color3_button = tk.Button(pick_color_frame, text='color3', fg='Purple', command=image.set_color3)
    color3_button.pack(side=tk.LEFT)
    ball_button = tk.Button(pick_color_frame, text='ball', fg='Yellow', command=image.set_ball)
    ball_button.pack(side=tk.LEFT)

    exit_button = tk.Button(instruction_frame, text='READY', fg='Black', command=ready_func)
    exit_button.pack(side=tk.LEFT)
    exit_button = tk.Button(instruction_frame, text='START', fg='Black', command=start_func)
    exit_button.pack(side=tk.LEFT)
    exit_button = tk.Button(instruction_frame, text='PAUSE', fg='Black', command=pause_func)
    exit_button.pack(side=tk.LEFT)
    rest_button = tk.Button(instruction_frame, text='REST', fg='Black', command=rest_func)
    rest_button.pack(side=tk.LEFT)
    field_button = tk.Button(instruction_frame, text='field', fg='Black', command=image.set_field)
    field_button.pack(side=tk.LEFT)
    side_button = tk.Button(instruction_frame, text='side', fg='Black', command=side_func)
    side_button.pack(side=tk.LEFT)
    defend_button = tk.Button(instruction_frame, text='後攻', fg='Red', command=def_wait)
    defend_button.pack(side=tk.LEFT)
    PK_button = tk.Button(instruction_frame, text='PK', fg='Red', command=PK_func)
    PK_button.pack(side=tk.LEFT)
    correct_button = tk.Button(instruction_frame, text='projection', fg='Black', command=image.set_correct)
    correct_button.pack(side=tk.LEFT)
    mask_button = tk.Button(instruction_frame, text='mask', fg='Black', command=image.set_mask)
    mask_button.pack(side=tk.LEFT)
    print_button = tk.Button(instruction_frame, text='Print', fg='Black', command=print_func)
    print_button.pack(side=tk.LEFT)
    exit_button = tk.Button(instruction_frame, text='exit', fg='Black', command=exit_func)
    exit_button.pack(side=tk.LEFT)

    window.mainloop()
