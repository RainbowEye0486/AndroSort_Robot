"""
A simple USB to nRF module data sender
"""

import serial
import serial.tools.list_ports
import multiprocessing
from multiprocessing import Process, Queue
import time
import platform
from datetime import datetime
import json
import os

if 'Linux' in platform.system():
    from getch import getch
# elif 'Windows' in platform.system():
# from msvcrt import getwch as getch
else:
    from getch import getch

'''
# Old version with mismatches
NONE        = 'N', 0     # Move
LSHOOT      = 'u', 1     # Left Foot Shoot
RSHOOT      = 'i', 2     # Right Foot Shoot
ur strings (like \n)
    if you know in advance how many characters to read, repeat reading until you've received them all

In both cases, specify a timeout (for example 1 second) when opening the serial line, to get back control on your code if the remote end doesn't send anything for whatever reason.
LPASS       = 'o', 3     # Left Foot Pass
RPASS       = 'p', 4     # Right Foot Pass
# MSHOOT      = 'm', 3     # Middle Foot Shoot
DEFENCE     = 'y', 5     # Dodge
STAND       = 'Y', 6     # Stand Up
REST        = 'x', 7     # Dodge

FFORWARD    = 'W', 0     # Fast Forward
FORWARD     = 'w', 1     # Forward
BACKWARD    = 's', 2     # Backward
MOVE_LEFT   = 'a', 3     # Shift Left
MOVE_RIGHT  = 'd', 4     # Shift Right
FMOVE_LEFT  = 'A', 5     # Fast Shift Left
FMOVE_RIGHT = 'D', 6     # Fast Shift Right
TRUN_LEFT   = 'q', 7     # Turn Left
TRUN_RIGHT  = 'e', 8     # Turn Right
'''

cfg = None
DEF_port = 'COM14'
DEF_baud = 9600


def inputFunc(q):
    """
    Multi processing function, get input

    Parameters
        param1 - A multiprocess queue to push new input data

    Raise
        input character not valid

    Description
        a new character will be pushed only when queue is empty
    """
    while True:
        try:
            input_data = getch()
            if q.empty():
                q.put(input_data)
                time.sleep(0.001)
            if ord(input_data) in [3]:
                break
        except OverflowError:
            print('enter invalid value')


def read_config():
    """
    Read configuration json file

    Return
        retva1 - config dictionary data structure
    """
    global cfg
    config = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config, 'r') as f:
        cfg = json.load(fp=f)


def load_cfg(config):
    """
    Load config from other program

    Parameters
        param1 - outer config dictionary data structure
    """
    global cfg
    cfg = config


def device_read(device, delay=0):
    """
    Reading nRF input after delay

    Parameters
        param1 - nRF serial device
        param2 - read after this delay

    Return
        retva1 - decode data (in gbk)
        retva2 - length

    Raise
        decode error
    """
    time.sleep(delay)
    a = device.in_waiting
    if a > 0:
        data = device.read(a)
        try:
            decode_data = bytes.decode(data, "gbk")
        except Exception:
            print('Decode error. Maybe data too long or reading time too short')
            return "None", a
        else:
            return decode_data, a
    return "None", a


def download_cfg(device):
    for i in range(len(cfg["RESET"]) - 3):
        print(str(i + 1) + ' ' + str(cfg["RESET"]["default" + str(i + 1)]))

    choose_cfg = input("Enter desired address >>> ")
    if choose_cfg.isdigit():
        if int(choose_cfg) > len(cfg["RESET"]) - 3:
            print("No such cfg, abort......")
            return
    address_select = "default" + choose_cfg

    device.write(bytes(cfg["CMD"]["Freq"] + cfg["RESET"]["Freq"], encoding='utf8'))
    data, __ = device_read(device, 0.5)
    if "成功" in data:
        print('freq setting success')
    print(data)
    device.write(bytes(cfg["CMD"]["Rate"] + cfg["RESET"]["Rate"], encoding='utf8'))
    data, __ = device_read(device, 0.5)
    if "成功" in data:
        print('rate setting success')
    print(data)
    device.write(bytes(cfg["CMD"]["RXA"] + cfg["RESET"][address_select]["RXA"], encoding='utf8'))
    data, __ = device_read(device, 0.5)
    if "成功" in data:
        print('rxa setting success')
    print(data)
    device.write(bytes(cfg["CMD"]["TXA"] + cfg["RESET"][address_select]["TXA"], encoding='utf8'))
    data, __ = device_read(device, 0.5)
    if "成功" in data:
        print('txa setting success')
    print(data)


# def RF_sendCmd(input_data, device, delay=0, mode=0):
#     """
#     Send command through RF

#     Parameters
#         param1 - data to send
#         param2 - serial device to use
#         param3 - delay before sending
#         param4 - sending mode

#     Description
#         For mode(@param4) 0, program will extend input character into robot command format and then send
#         For mode(@param4) 1, program will directly send what it received
#     """
#     time.sleep(delay)
#     current_time = datetime.now().strftime("%H-%M-%S-%f")
#     if mode == 0:
#         send_data = '#'+input_data+'1'+input_data+'2'+input_data+'9' +'$'
#         print(current_time + " Send=", send_data.encode())
#         device.write(bytes(send_data, encoding='utf8'))
#     else:
#         print(current_time + " Send=", input_data.encode())
#         device.write(bytes(input_data, encoding='utf8'))


def RF_sendCmd(input_data, device, robotID, delay=0, mode=0):
    """
    Send command through RF

    Parameters
        param1 - data to send
        param2 - serial device to use
        param3 - delay before sending
        param4 - sending mode

    Description
        For mode(@param4) 0, program will extend input character into robot command format and then send
        For mode(@param4) 1, program will directly send what it received
    """
    time.sleep(delay)
    current_time = datetime.now().strftime("%H-%M-%S-%f")
    if mode == 0:
        send_data = '#' + input_data + '1' + input_data + '1'+ input_data + '1' +'$'
        # send_data = '#' + robotID + input_data + '1'+'$'
        print(current_time + " Send=", send_data.encode())
        device.write(bytes(send_data, encoding='utf8'))
    else:
        print(current_time + " Send=", input_data.encode())
        device.write(bytes(input_data, encoding='utf8'))


def get_device():
    """
    Obtain the device connected to computer
    """
    ports = serial.tools.list_ports.comports()
    port_list = [port.device for port in ports]
    return port_list


def open_device(portname):
    """
    Scanning through baudrate in the cfg file and existing port

    Parameters
        param1 - name of the port to test

    Return
        retva1 - device open or not
        retva2 - serial device object (None if not opened)
        retva3 - opened device baudrate (0 if not opened)
    """
    for baud in cfg['Scan']:
        print(portname, ' Scanning Baudrate: ', baud, end="")

        device = serial.Serial(portname, timeout=0.5, baudrate=baud)
        device.write(bytes(cfg['CMD']['Info'], encoding='utf8'))
        data, __ = device_read(device, 0.5)
        if 'OK' == data[0:2]:
            print('......Success')
            print("Device %s Baudrate: %s found" % (device.name, baud))
            return 1, device, baud
        else:
            print('......Failed')
        device.close()
    print('Error --Cannot open serial device')
    return 0, None, 0


def device_chose():
    """
    The program to teach user how to choose

    Return
        retva1 - device open or not
        retva2 - serial device object (None if not opened)
        retva3 - opened device baudrate (0 if not opened)
    """
    port_list = get_device()
    list_len = len(port_list)

    if list_len == 0:
        print("No serial device found")
        return 0, None, 0
    else:
        print("Choose device below......")

    for i in range(0, list_len):
        print('%s %s' % (i + 1, port_list[i]))

    choose_device = None
    while True:
        # Get user input
        input_num = input("Enter device number (or q to quit)>>> ")

        if input_num.isdigit():
            choose = int(input_num)
            if choose > list_len:
                print('Device not found')
                continue
            else:
                choose_device = choose - 1
                break
        else:
            if 'q' == input:
                print('Aborting......')
                return 0, None, 0
    state, device, baud = open_device(port_list[choose_device])
    return state, device, baud


def main_procedure(device):
    """
    Main function of the nRF control

    Parameters
        param1 - port to open. If not open then use COM14
        param2 - baud to use. If not given then use 9600

    Description
        Press 'space' to seitch between FREE mode and robot controller mode
        One can use FREE mode to send any character, string or even send AT
        command to currently using module
    """
    q = Queue(5)
    pro = Process(target=inputFunc, args=(q,))
    pro.daemon = True

    pro.start()

    mode = 0
    saved = ''
    while True:
        tstart = time.time()
        current_time = datetime.now().strftime("%H-%M-%S-%f")
        if not q.empty():
            # Get input from queue
            input_data = q.get()

            # End of program
            if ord(input_data) in [3]:
                print(current_time + ' End of program')
                break

            # Switch mode
            elif input_data == ' ':
                saved = ''
                mode = 1 if mode == 0 else 0
                print(current_time + ' Switch to {} mode'.format('FREE' if mode == 1 else 'ROBOT COMMAND'))
            else:
                if mode == 0:
                    print(current_time + ' Has new input: ', ord(input_data), input_data)
                    RF_sendCmd(input_data, device, '1', 0.05, mode)
                else:
                    if ord(input_data) == 10 or ord(input_data) == 13:
                        RF_sendCmd(saved, device, '1', 0.05, mode)
                        saved = ''
                        time.sleep(0.5)
                    else:
                        saved = saved + input_data
                        print(input_data)

        while time.time() - tstart < 1 / 30:
            # Read input
            data, length = device_read(device)
            if length != 0:
                current_time = datetime.now().strftime("%H-%M-%S-%f")
                print(current_time + ' ' + data)


def communicate(device, que):
    mode = 0
    tstart = time.time()
    current_time = datetime.now().strftime("%H-%M-%S-%f")
    if not que.empty():
        # Get input from queue
        input_data = que.get()
        robotID = input_data[1]
        input_data = input_data[0]
        # print(current_time + ' Has new input: ', ord(input_data), input_data)
        RF_sendCmd(input_data, device, robotID, 0.05, mode)
    while time.time() - tstart < 1 / 30:
        # Read input
        data, length = device_read(device)
        if length != 0:
            current_time = datetime.now().strftime("%H-%M-%S-%f")
            print(current_time + ' ' + data)


def device_close(device):
    if device is None:
        return
    else:
        device.close()


if __name__ == '__main__':
    read_config()
    state, device, baud = device_chose()
    if state == 1:
        download_cfg(device)
        main_procedure(device)
