/*
R#action.ino
Ernie Wang
erniewangtw@gmail.com.tw

Copyright (c) 2019 aiRobot, NCKU

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

void R4Action() {
    switch (cmd) {
      /*R5forward*/
  case CMD_FORWARD: {
            uint8_t jumpFlag = 0;
            SetFrameRun(0, 150);
            SetFrameRun(2, 50);
            do {
                //        SetFrameRun(2, 100);
                SetFrameRun(3, 50);
                SetFrameRun(4, 50);

                if ((cmd = getData()) != CMD_FORWARD) {
                    jumpFlag = 1;
                    break;
                }
                //        SetFrameRun(61, 100);
                SetFrameRun(5, 50);
                SetFrameRun(6, 50);
            } while ((cmd = getData()) == CMD_FORWARD);

            if (jumpFlag == 1) {
                SetFrameRun(9, 50);
            }
            else {
                SetFrameRun(7, 50);
            }

            SetFrameRun(1, 500);

            pos_delay_count = pos_delay_set;
        } break;
  


///////////////////////no R4 config file//////////////////////////////
        case CMD_FFORWARD: {
            uint16_t jumpFlag = 0;
            SetFrameRun(0, 150);
            SetFrameRun(2, 50);
            SetFrameRun(52, 100);//70
            SetFrameRun(53, 45);//71
            do {
                SetFrameRun(51, 200);//72
                SetFrameRun(55, 25);//73

                if ((cmd = getData()) != CMD_FFORWARD) {
                    jumpFlag = 1;
                    break;
                }

                SetFrameRun(57, 200);//74
                SetFrameRun(58, 25);//75
            } while ((cmd = getData()) == CMD_FFORWARD);

            SetFrameRun(1, 100);
            pos_delay_count = pos_delay_set;
        } break;

        case CMD_BACKWARD: {
            uint8_t jumpFlag = 0;

            SetFrameRun(0, 150);
            SetFrameRun(2, 50);
            do {
                SetFrameRun(7, 85);
                SetFrameRun(10, 115);

                if ((cmd = getData()) != CMD_BACKWARD) {
                    jumpFlag = 1;
                    break;
                }
                SetFrameRun(9, 85);
                SetFrameRun(8, 115);
            } while ((cmd = getData()) == CMD_BACKWARD);

            if (jumpFlag == 1) {
                SetFrameRun(5, 80);
            }
            else {
                SetFrameRun(3, 80);
            }

            SetFrameRun(1, 10);
            pos_delay_count = pos_delay_set;
        } break;

        case CMD_TRUN_LEFT:
            do {
#ifdef OLD_TURN
                SetFrameRun(13, 25);
                SetFrameRun(11, 75);
#else
                SetFrameRun(11, 25);
                SetFrameRun(12, 38);
                SetFrameRun(1, 80);
#endif
            } while ((cmd = getData()) == CMD_TRUN_LEFT);
            SetFrameRun(1, 10);
            break;

        case CMD_TRUN_RIGHT:
            do {
#ifdef OLD_TURN
                SetFrameRun(12, 25);
                SetFrameRun(11, 75);
#else
                SetFrameRun(11, 25);
                SetFrameRun(13, 38);
                SetFrameRun(1, 80);
#endif
            } while ((cmd = getData()) == CMD_TRUN_RIGHT);
            SetFrameRun(1, 10);
            pos_delay_count = pos_delay_set;
            break;

        case CMD_FTRUN_LEFT:
            do {
#ifdef OLD_TURN
                SetFrameRun(13, 25);
                SetFrameRun(11, 75);
#else
                SetFrameRun(11, 25);
                SetFrameRun(12, 125);
                SetFrameRun(1, 10);
#endif
                SetFrameRun(1, 100);
            } while ((cmd = getData()) == CMD_FTRUN_LEFT);
            SetFrameRun(1, 10);
            break;

        case CMD_FTRUN_RIGHT:
            do {
#ifdef OLD_TURN
                SetFrameRun(12, 25);
                SetFrameRun(11, 75);
#else
                SetFrameRun(11, 25);
                SetFrameRun(13, 125);
                SetFrameRun(1, 10);
#endif
                SetFrameRun(1, 100);
            } while ((cmd = getData()) == CMD_FTRUN_RIGHT);
            SetFrameRun(1, 10);
            pos_delay_count = pos_delay_set;
            break;

        case CMD_MOVE_LEFT:
            do {
                SetFrameRun(15, 30);
                SetFrameRun(14, 70);
            } while ((cmd = getData()) == CMD_MOVE_LEFT);
            SetFrameRun(1, 10);
            pos_delay_count = pos_delay_set;
            break;

        case CMD_FMOVE_LEFT:
            do {
                SetFrameRun(17, 230);
                SetFrameRun(19, 70);
            } while ((cmd = getData()) == CMD_FMOVE_LEFT);
            SetFrameRun(19, 350);
            SetFrameRun(1, 120);
            pos_delay_count = pos_delay_set;
            break;

        case CMD_MOVE_RIGHT:
            do {
                SetFrameRun(16, 30);
                SetFrameRun(14, 70);
            } while ((cmd = getData()) == CMD_MOVE_RIGHT);
            SetFrameRun(1, 10);
            pos_delay_count = pos_delay_set;

            break;

        case CMD_FMOVE_RIGHT:
            do {
                SetFrameRun(18, 230);
                SetFrameRun(19, 70);
            } while ((cmd = getData()) == CMD_FMOVE_RIGHT);
            SetFrameRun(19, 350);
            SetFrameRun(1, 120);
            pos_delay_count = pos_delay_set;

            break;

        case CMD_RFSHOOT:
            do {
                SetFrameRun(0, 150);
                SetFrameRun(65, 100);
                SetFrameRun(66, 50);
                SetFrameRun(67, 100);
                SetFrameRun(5, 50);
            } while ((cmd = getData()) == CMD_RFSHOOT);
            SetFrameRun(1, 50);
            break;

        case CMD_LFSHOOT:
            do {
                SetFrameRun(0, 150);
                SetFrameRun(75, 100);
                SetFrameRun(76, 50);
                SetFrameRun(77, 100);
                SetFrameRun(3, 50);
            } while ((cmd = getData()) == CMD_LFSHOOT);
            SetFrameRun(1, 50);
            pos_delay_count = pos_delay_set;
            break;

        case CMD_RSSHOOT:
            do {
                SetFrameRun(37, 200);
                SetFrameRun(39, 100);
                SetFrameRun(40, 300);
                SetFrameRun(16, 30);
                SetFrameRun(14, 70);
                SetFrameRun(15, 30);
                SetFrameRun(14, 70);
            } while ((cmd = getData()) == CMD_RSSHOOT);
            SetFrameRun(1, 100);
            break;

        case CMD_LSSHOOT:
            do {
                //        SetFrameRun(0, 300);
                SetFrameRun(31, 200);
                //        SetFrameRun(32, 50);
                SetFrameRun(33, 100);
                SetFrameRun(34, 300);
                SetFrameRun(15, 30);
                SetFrameRun(14, 70);
                SetFrameRun(16, 30);
                SetFrameRun(14, 70);

            } while ((cmd = getData()) == CMD_LSSHOOT);
            //      SetFrameRun(3, 50);
            //      SetFrameRun(0, 25);
            SetFrameRun(1, 100);
            pos_delay_count = pos_delay_set;
            break;

        case CMD_RBSHOOT:
            do {
                SetFrameRun(0, 150);
                SetFrameRun(65, 100);
                SetFrameRun(71, 50);
                SetFrameRun(72, 100);
                SetFrameRun(5, 50);

            } while ((cmd = getData()) == CMD_RBSHOOT);
            SetFrameRun(1, 50);
            break;

        case CMD_LBSHOOT:
            do {
                SetFrameRun(0, 150);
                SetFrameRun(75, 100);
                SetFrameRun(73, 50);
                SetFrameRun(74, 100);
                SetFrameRun(3, 50);

            } while ((cmd = getData()) == CMD_LBSHOOT);
            SetFrameRun(1, 50);
            pos_delay_count = pos_delay_set;
            break;

        case CMD_RPASS:
            SetFrameRun(1, 150);
            do {
                SetFrameRun(0, 150);
                SetFrameRun(65, 50);
                SetFrameRun(44, 180);
                SetFrameRun(5, 10);
            } while ((cmd = getData()) == CMD_RPASS);
            SetFrameRun(1, 150);
            pos_delay_count = pos_delay_set;
            break;

        case CMD_LPASS:
            SetFrameRun(1, 150);
            do {
                SetFrameRun(0, 150);
                SetFrameRun(75, 50);
                SetFrameRun(45, 180);
                SetFrameRun(3, 10);
            } while ((cmd = getData()) == CMD_LPASS);
            SetFrameRun(1, 150);
            pos_delay_count = pos_delay_set;
            break;

        case CMD_F_DEFENSE:
            SetFrameRun(86, 400);
            SetFrameRun(87, 500);
            do {
                SetFrameRun(88, 1400);
            } while ((cmd = getData()) == CMD_F_DEFENSE);
            SetFrameRun(1, 100);
            pos_delay_count = pos_delay_set;
            break;

        case CMD_R_DEFENSE:
            SetFrameRun(80, 500);
            do {
                SetFrameRun(81, 1500);
            } while ((cmd = getData()) == CMD_R_DEFENSE);
            SetFrameRun(82, 300);
            SetFrameRun(1, 100);
            pos_delay_count = pos_delay_set;
            break;

        case CMD_L_DEFENSE:
            SetFrameRun(83, 500);
            do {
                SetFrameRun(84, 1500);
            } while ((cmd = getData()) == CMD_L_DEFENSE);
            SetFrameRun(85, 300);
            SetFrameRun(1, 100);
            pos_delay_count = pos_delay_set;
            break;

        default:
            //      Serial.println("CMD not found");
            break;
    }
}
