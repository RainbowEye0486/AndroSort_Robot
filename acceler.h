/*
acceler.h
Gatsby Jan
gatsby.jan@ppt.com.tw

Copyright (c) 2018 ~ 2019 CreatorArk technology

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

#ifndef __ACCELER_H__
#define __ACCELER_H__

// for GY-61  (ADXL335)

#include "peripheral.h"

#define ACCE_DIR_X 0
#define ACCE_DIR_Y 1
#define ACCE_DIR_Z 2
#define STAND_THRES 40

// Get up var
#define Acce_z acce_getDirValue(PP_SENSOR_TYPE_ACCELER, ACCE_DIR_Z)
#define Acce_y acce_getDirValue(PP_SENSOR_TYPE_ACCELER, ACCE_DIR_Y)
#define Acce_x acce_getDirValue(PP_SENSOR_TYPE_ACCELER, ACCE_DIR_X)


#if ROBOT_ID == 1
int acc_offset[] = {508, 403, 510};
#elif ROBOT_ID == 2
int acc_offset[] = {505, 400, 518};
#elif ROBOT_ID == 3
int acc_offset[] = {499, 408, 505};
#elif ROBOT_ID == 4
int acc_offset[] = {506, 404, 504};
#elif ROBOT_ID == 5
int acc_offset[] = {506, 403, 513};
#elif ROBOT_ID == 6
int acc_offset[] = {508, 403, 510};
#elif ROBOT_ID == 7
int acc_offset[] = {502, 403, 504};
#else
#endif

enum body_status {
    STAND = 0,
    FALL_FORWARD,
    FALL_BACK,
    FALL_LEFT,
    FALL_RIGHT,
    TOTAL
};

uint16_t status_count[6] = {};

bool getup_flag = false;

int16_t acce_init(uint8_t id);
int16_t acce_enable(uint8_t id);
int16_t acce_disable(uint8_t id);
int16_t acce_getDirValue(uint8_t id, uint8_t dir);
void check_body_status();

#endif  // __ACCELER_H__
