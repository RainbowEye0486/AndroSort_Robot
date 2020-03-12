import time
from threading import Thread
from Vision import Image_Identifier as image
from Strategy import challenge_2
from comm import nrf_controller as nrf
from queue import Queue
import platform


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


def Main_thread():
    global stop_strategy
    while True:
        command_main = input()
        if command_main == "s":
            print(stop_strategy)
            stop_strategy = ~stop_strategy
            time.sleep(0.1)
            print(stop_strategy)


def Image_thread():
    image.image_func()


def Challenge2_thread(que):
    #  first set field coordinate
    global stop_strategy
    challenge_2.Initialize()
    challenge_2.strategy_update_field(side, image.field_pos, image.middle, image.penalty_pos)
    while True:
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
                print('cmd:', input_data)
                if que.empty():
                    que.put(input_data)
                    # que.put('w1')  # test
                    time.sleep(0.001)
                else:
                    que.get()
                    que.put(input_data)
                    time.sleep(0.001)
            except OverflowError:
                print('invalid cmd value')
        time.sleep(0.01)


def NRF_thread(device, que):
    while True:
        nrf.communicate(device, que)
        time.sleep(0.01)


if __name__ == '__main__':
    nrf.read_config()
    state, device, baud = nrf.device_chose()
    if state == 1:
        nrf.download_cfg(device)
        cmd_in_wait = Queue(5)
        main_thread = Thread(target=Main_thread, name='Ma_Tr')
        thread1 = Thread(target=Image_thread, name='Im_Tr')
        thread1.start()
        time.sleep(0.5)
        main_thread.start()
        image.return_field()
        if challenge_num == 2:
            thread2 = Thread(target=Challenge2_thread, name='C2_Tr', args=(cmd_in_wait,))
            thread2.start()
            time.sleep(0.5)
            thread3 = Thread(target=NRF_thread, name='Comm_Tr', args=(device, cmd_in_wait,))
            thread3.start()
            time.sleep(0.5)
