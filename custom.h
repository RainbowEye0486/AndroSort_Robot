/*
custom.h
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

#ifndef __CUSTOM_H__
#define __CUSTOM_H__

// for input mode
// enum{
//  BTN_MODE_GAMEPAD = 0,
//  BTN_MODE_BT,
//  BTN_MODE_AUTO,
//  BTN_MODE_NONE
//};

// for auto mode
// enum{
//  AUTOKEY_DIR_RIGHT = 1,
//  AUTOKEY_DIR_BACKWARD, // 2
//  AUTOKEY_DIR_LEFT,     // 3
//  AUTOKEY_DIR_FORWARD,  // 4
//  AUTOKEY_TRIANGLE,     // 5
//  AUTOKEY_CIRCLES,      // 6
//  AUTOKEY_CROSS,        // 7
//  AUTOKEY_SQUARE,       // 8
//  AUTOKEY_L1,           // 9
//  AUTOKEY_R1,           // 10
//  AUTOKEY_L2,           // 11
//  AUTOKEY_R2,           // 12
//  AUTOKEY_SELECT,       // 13
//  AUTOKEY_START,        // 14
//  AUTOKEY_L3,           // 15
//  AUTOKEY_R3,           // 16
//  AUTOKEY_MAX
//};

// for auto mode
//#define SENSOR_IR_EDGE  120
//#define SENSOR_SONAR_FIGHT  40

//#define AUTO_GET_DATA_CNT_MAX 4

//#define AUTO_ACCE_Z_FACE_DOWM_MAX 580
//#define AUTO_ACCE_Z_FACE_UP_MAX 420
void custom_setup();

void custom_loop();

void cmdSetup();
void checkAcce();

#endif
