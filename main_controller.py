import time
from threading import Thread
from Vision import Image_Identifier as image
from Strategy import challenge_2
from comm import nrf_controller as nrf


image_buffer = list()
decision_done = False
# 需要調整參數
side = 0  # attacking side
challenge_num = 2


def Main_thread():
    while True:
        #print(image.return_motion())
        time.sleep(1)


def Image_thread():
    image.image_func()


def Challenge2_thread():
    #  first set field coordinate
    challenge_2.strategy_update_field(side, image.field_pos, image.middle, image.penalty_pos)
    while True:
        challenge_2.Update_Robo_Info(image.our_dir, image.our_data, image.enemy_data, image.ball_pos_now)
        # print(image.our_dir)
        # print(image.our_data)
        # print(image.enemy_data)
        # print(image.ball_pos_now)
        cmd = challenge_2.strategy()


if __name__ == '__main__':
    nrf.read_config()
    state, device, baud = nrf.device_chose()
    if state == 1:
        nrf.download_cfg(device)
    main_thread = Thread(target=Main_thread, name='Ma_Tr')
    thread1 = Thread(target=Image_thread, name='Im_Tr')
    thread1.start()
    time.sleep(0.5)
    main_thread.start()
    image.return_field()
    if challenge_num == 2:
        thread2 = Thread(target=Challenge2_thread, name='C2_Tr')
        thread2.start()
