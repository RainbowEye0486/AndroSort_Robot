/*
action.ino
Ernie Wang
erniewangtw@gmail.com.tw

Copyright (c) 2019 Ernie Wang

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/

#include "action.h"
#include "acceler.h"

uint8_t getData() {
    return rf24_getData(PP_SENSOR_TYPE_RF24KEY);
}

void doAction() {
    switch (cmd = getData()) {
        case CMD_START:
            if (!started) {
                uart_firstStartMotor();
                SetFrameRun(1, 200);
                started = 1;
                pos_delay_count = pos_delay_set;
            }
            break;

        case CMD_STOP:
            uart_disableMotor();
            started = 0;
            break;

        default:
            if (cmd == CMD_PK) {
                if (!started) {
                    uart_firstStartMotor();
                    SetFrameRun(1, 1000);
                    started = 1;
                }
                PK_MODE = true;
                SetFrameRun(60, 500);
                uart_disableMotor();
                while (true) {
                    cmd = getData();
                    if (cmd == CMD_DEFENSE || cmd == CMD_F_DEFENSE || cmd == CMD_STOP ||
                        cmd == CMD_R_DEFENSE || cmd == CMD_L_DEFENSE)
                        break;
                }
                PK_MODE = false;
            }
            if (started) {
                switch (cmd) {
                    case CMD_DEFENSE:
                        do {
                            SetFrameRun(60, 2000);
                        } while ((cmd = getData()) == CMD_DEFENSE);
                        SetFrameRun(1, 100);
                        pos_delay_count = pos_delay_set;
                        break;

                    case CMD_REST:
                        uart_disableMotor();
                        break;

                    case CMD_STAND:
                        SetFrameRun(1, 1000);
                        pos_delay_count = pos_delay_set;
                        break;

                    default:
                        indAction();
                        break;
                }
            }

            break;
    }
}

void indAction() {
#if ROBOT_ID == 1
    R1Action();
#elif ROBOT_ID == 2
    R2Action();
#elif ROBOT_ID == 3
    R3Action();
#elif ROBOT_ID == 4
    R4Action();
#elif ROBOT_ID == 5
    R5Action();
#elif ROBOT_ID == 6
    R6Action();
#elif ROBOT_ID == 7
    R7Action();
#else
#endif
}

void getUp(uint16_t body_status) {
    getup_flag = true;
    switch(body_status) {
        case FALL_FORWARD:
            // forward get up
            SetFrameRun(19, 100);
            SetFrameRun(20, 300);
            SetFrameRun(21, 300);
            SetFrameRun(22, 250);
            SetFrameRun(23, 250);
            SetFrameRun(24, 1400);
            SetFrameRun(25, 500);
            SetFrameRun(1, 200);
            move_num = 0;
            break;
        case FALL_BACK:
            // backward get up
            SetFrameRun(26, 100);
            SetFrameRun(27, 200);
            SetFrameRun(28, 400);
            SetFrameRun(29, 1400);
            SetFrameRun(25, 400);
            SetFrameRun(1, 200);
            move_num = 0;
            break;
        case FALL_LEFT:
            
            SetFrameRun(24, 700);

            break;
        case FALL_RIGHT:
        
            SetFrameRun(24, 700);

            break;
        default:
            break;
    }
    getup_flag = false;
}

void steady() {
    int16_t acce_z = Acce_z;
    if (abs(acce_z) > 30) {
        SetFrameRun(48, 1000);
        SetFrameRun(49, 500);
    }
}
