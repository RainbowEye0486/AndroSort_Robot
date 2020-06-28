/*
peripheral.h
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

#ifndef __PERIPHERAL_H__
#define __PERIPHERAL_H__

enum PP_IO_TYPE {
    PP_TYPE_GPIO = 0,
    PP_TYPE_I2C,
    PP_TYPE_ADC,
    PP_TYPE_SONAR,
    PP_TYPE_MAX
};

enum PP_SENSOR_TYPE {
    //  PP_SENSOR_TYPE_ULTRASONIC_0 = 0,
    //  PP_SENSOR_TYPE_ULTRASONIC_1,  // 1
    //  PP_SENSOR_TYPE_ULTRASONIC_2,  // 2
    //  PP_SENSOR_TYPE_ULTRASONIC_3,  // 3
    PP_SENSOR_TYPE_ACCELER,  // 4
                             //  PP_SENSOR_TYPE_IR_0,    // 5
                             //  PP_SENSOR_TYPE_IR_1,    // 6
                             //  PP_SENSOR_TYPE_GAMEPAD, // 7
                             //  PP_SENSOR_TYPE_BTKEY,   // 8
    PP_SENSOR_TYPE_RF24KEY,  // 9
    PP_SENSOR_TYPE_MAX
};

enum PP_SENSOR_GET {
    //  PP_SENSOR_GET_ULTRASONIC_0 = 0,
    //  PP_SENSOR_GET_ULTRASONIC_1,   // 1
    //  PP_SENSOR_GET_ULTRASONIC_2,   // 2
    //  PP_SENSOR_GET_ULTRASONIC_3,   // 3
    PP_SENSOR_GET_ACCELER_X,  // 4
    PP_SENSOR_GET_ACCELER_Y,  // 5
    PP_SENSOR_GET_ACCELER_Z,  // 6
                              //  PP_SENSOR_GET_IR_0,           // 7
                              //  PP_SENSOR_GET_IR_1,           // 8
                              //  PP_SENSOR_GET_GAMEPAD,        // 9
                              //  PP_SENSOR_GET_BTKEY,          // 10
    PP_SENSOR_GET_MAX
};

typedef struct {
    uint8_t isEnable;
    PP_SENSOR_TYPE sensorType;
    PP_IO_TYPE ioType;
} pp_type;

#define PP_SENSOR_MAX 10
extern pp_type pp_sensor[PP_SENSOR_MAX];

// GPIO
//#define US_ECHO_3     5
//#define US_TRIGGER_3  6
//#define US_TRIGGER_1  7
//#define US_ECHO_1     8
//#define US_TRIGGER_0  9
//#define US_ECHO_0     10
//#define US_ECHO_2     11
//#define US_TRIGGER_2  12

// ADC
#define ACCE_X_PIN A0
#define ACCE_Y_PIN A1
#define ACCE_Z_PIN A2
#define BAT_DETEC_PIN A3
#define CMD_PIN A5
//#define IR_PIN_1        A5

#endif  // __PERIPHERAL_H__
