import time
from tkinter import *
from threading import Thread
from Vision import Image_Identifier as image
from Strategy import challenge_2
from comm import nrf_controller as nrf
from queue import Queue
import platform
import tkinter as tk

start_bit = 0

if 'Linux' in platform.system():
    from getch import getch
elif 'Windows' in platform.system():
    from msvcrt import getwch as getch
else:
    from getch import getch

image_buffer = list()
decision_done = False
# 需要調整參數
side = 0  # attacking side
challenge_num = 2
stop_strategy = True


def start_func():
    global start_bit
    start_bit = 1


def pause_func():
    global start_bit
    start_bit = 0


def exit_func():
    window.destroy()
    image.exit_bit = 1
    sys.exit(0)


def Image_thread():
    image.image_func()


def Challenge2_thread(que):
    #  first set field coordinate
    global stop_strategy
    challenge_2.Initialize()
    challenge_2.strategy_update_field(side, image.field_pos, image.middle, image.penalty_pos)
    while start_bit == 1:
        """print("our direction", image.our_dir)
        print("our position", image.our_data)
        print("enemy position", image.enemy_data)
        print("ball position", image.ball_pos_now)"""
        # print("enemy position", image.enemy_data)
        if stop_strategy < 0:
            challenge_2.Update_Robo_Info(image.our_dir, image.our_data, image.enemy_data, image.ball_pos_now)
            cmd = challenge_2.strategy()
            try:
                input_data = cmd[0]
                # print('cmd:', input_data)
                if que.empty():
                    que.put(input_data)
                    # que.put('w1')  # test
                    time.sleep(0.001)
                else:
                    if input_data[0] == 'N':
                        time.sleep(1)
                    else:
                        que.get()
                        que.put(input_data)
                        time.sleep(0.001)
            except OverflowError:
                print('invalid cmd value')
            # print('ch2', (time.time() - lasttime)*1000)
        time.sleep(0.01)


def NRF_thread(device, que):
    while True:
        # lasttime = time.time()
        nrf.communicate(device, que)
        time.sleep(0.01)
        # print('NRF', (time.time() - lasttime)*1000)


if __name__ == '__main__':

    thread1 = Thread(target=Image_thread, name='Im_Tr')
    thread1.start()
    time.sleep(0.5)

    nrf.read_config()
    state, device, baud = nrf.device_chose()
    if state == 1:
        nrf.download_cfg(device)
        cmd_in_wait = Queue(5)
        thread1 = Thread(target=Image_thread, name='Im_Tr')
        thread1.start()
        time.sleep(0.5)
        image.return_field()
        if challenge_num == 2:
            thread2 = Thread(target=Challenge2_thread, name='C2_Tr', args=(cmd_in_wait,))
            thread2.start()
            time.sleep(0.5)
            thread3 = Thread(target=NRF_thread, name='Comm_Tr', args=(device, cmd_in_wait,))
            thread3.start()
            time.sleep(0.5)

    # all the setting of button
    window = tk.Tk()
    pick_color_frame = tk.Frame(window)
    pick_color_frame.pack()
    instruction_frame = tk.Frame(window)
    instruction_frame.pack(side=tk.BOTTOM)

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

    exit_button = tk.Button(instruction_frame, text='START', fg='Black', command=start_func)
    exit_button.pack(side=tk.LEFT)
    exit_button = tk.Button(instruction_frame, text='PAUSE', fg='Black', command=pause_func)
    exit_button.pack(side=tk.LEFT)
    field_button = tk.Button(instruction_frame, text='field', fg='Black', command=image.set_field)
    field_button.pack(side=tk.LEFT)
    correct_button = tk.Button(instruction_frame, text='projection', fg='Black', command=image.set_correct)
    correct_button.pack(side=tk.LEFT)
    mask_button = tk.Button(instruction_frame, text='mask', fg='Black', command=image.set_mask)
    mask_button.pack(side=tk.LEFT)
    exit_button = tk.Button(instruction_frame, text='exit', fg='Black', command=exit_func)
    exit_button.pack(side=tk.LEFT)

    window.mainloop()
