/*
MainBoard_extend_micro.ino
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

#define ROBOT_ID 5  //------ Decide which robot to use, the general ID of the robot 
                    //------ Can choose from 1 to 7

uint16_t CMD_ID = 0;  //------ The ID of the robot, use to decide which command to recieve
                      //------ Can choose from 1 to 3
                      //------ Sqr => 1
                      //------ Bar => 2
                      //------ Tri => 3

#define USE_RF24 1  //------ Use nrf => 1 \
                    //------ Use serial => 0

#define ADDR_MODE 1   //------ Choose address
                      //------ 1 => BBCCDDEEFF, 06FFFFFFFF
                      //------ 2 => BBCCDDEEF0, F6FFFFFFFF
                      //------ 3 => B0C0D0E0F0, F1F2F3F4F5
                      //------ 4 => EE8FA92829, 92829AEE8F
                      //------ 5 => EE8FA92833, 92833AEE8F

//#define CHECK_ACC         //------ Use to check acc, which only print out acc

//#define OLD_TURN          //------ If the robot turn haven't been corrected

#define START_DELAY 3000  //------ The time delay for starting the robot
#define ACC_DELAY 1000  //------ The time delay for starting the robot

bool PK_MODE = false;

#if ROBOT_ID == 1
#include "motor_config/motorConfig_1/motor1.h"
#elif ROBOT_ID == 2
#include "motor_config/motorConfig_2/motor2_combine4.h"
#elif ROBOT_ID == 3
#include "motor_config/motorConfig_3/motor3.h"
#elif ROBOT_ID == 4
#include "motor_config/motorConfig_4/motor4.h"
#elif ROBOT_ID == 5
#include "motor_config/motorConfig_5/motor5.h"
#elif ROBOT_ID == 6
#include "motor_config/motorConfig_6/motor6.h"
#elif ROBOT_ID == 7
#include "motor_config/motorConfig_7/motor7_combine3.h"
#else
#endif

#include <stdint.h>
#include <string.h>
#include "acceler.h"
#include "action.h"
#include "custom.h"
#include "peripheral.h"
#include "rf24.h"

// The variable define the status of the robot
bool started = 0;

// For communication recieve
uint8_t rcev_buf[31] = {0};
uint16_t rcev_buf_size = 31;
uint16_t rcev_buf_count = 0;
void busy_delay(uint16_t limit, bool interupt = false);

// Variable for sending pass frames to motor
volatile uint16_t MotorPool[MOTOR_MOTOR_MAX][MOTOR_PARA_MAX] = {0x00};
volatile uint8_t isMotorUpgarad = 0;
volatile uint16_t motorPosMax = 2100, motorPosMin = 900;
volatile uint8_t Checksum_Calc;

// Variable for adjustment from adjust program
#define UART_CMDBUF_MAX 128
uint8_t uart_CmdBuf[UART_CMDBUF_MAX];
volatile uint16_t uart_CmdBufIdx = 0;
volatile uint8_t uart_isUartMode = 0;
volatile uint16_t uart_cmdIdx, uart_cmdChannel, uart_cmdEn, uart_cmdPos,
    uart_cmdTime;
volatile uint8_t uart_cmdSensorId;
volatile uint8_t uart_cmdMotorId;

//int countError = 0;
uint16_t move_num = 0;

// Function for able to pass adjustment to motor
int16_t uart_getCmd();
int16_t uart_checkCmd();
uint16_t strToInt(uint8_t* str, uint8_t len);
void UART_Send_Frame(uint16_t* FrameData);
void UART_Send_FrameByRom(uint16_t* FrameData);
// void UART_Send_FrameByRom( uint16_t * FrameData, uint16_t frame = 0xFF );

// For motor adjust to get sensor data
pp_type pp_sensor[PP_SENSOR_MAX] = {{0, PP_SENSOR_TYPE_ACCELER, PP_TYPE_ADC},
                                    {0, PP_SENSOR_TYPE_RF24KEY, 0}};

// Variable for system count
uint64_t init_tic = 0;  // The time system started
uint64_t acc_tic = 0;  // The time system started

void setup() {
    init_tic = millis();
    acc_tic = millis();

    pinMode(13, OUTPUT);  // For testing

    Serial.begin(115200);
    delay(200);
    Serial1.begin(500000);
    //  while(!Serial){;}     // DO NOT comment out the this unless the robot
    //  will work on the circumstance that USB connected
    while (!Serial1) {
        ;
    }

    timer1_init();  // Use to set the arduino timer, but usless in this version
    custom_setup();
}

void loop() {
    uint8_t motorChange = 0;

    // Run competition code
    custom_loop();

    // If the robot is in adjusting mode, which the USB is connected
    while (1) {
        if (uart_getCmd() == 0) {
            if (uart_checkCmd() == 0) {
                motorChange = 1;
            }
        }

        if (isMotorUpgarad == 1) {
            isMotorUpgarad = 0;
            if (motorChange == 1) {
                UART_Send_Frame(&MotorPool[0][0]);
            }
            motorChange = 0;

        }
    }
}  // loop

// Set Arduino timer, if you want to have different timer setting
void timer1_init() {
    cli();  // stop interrupts

    TCCR1A = 0;  // set entire TCCR1A register to 0
    TCCR1B = 0;  // same for TCCR1B
    TCNT1 = 0;   // initialize counter value to 0
    // set compare match register for 1hz increments
    // OCR1A = 15624;// = (16*10^6) / (60*1024) - 1 (must be <65536)
    OCR1A = 259;  // = (16*10^6) / (60*1024) - 1 (must be <65536)
    // turn on CTC mode
    TCCR1B |= (1 << WGM12);
    // Set CS10 and CS12 bits for 1024 prescaler
    TCCR1B |= (1 << CS12) | (1 << CS10);
    // enable timer compare interrupt
    TIMSK1 |= (1 << OCIE1A);

    sei();  // allow interrupts
}

uint8_t ledTestFlag = 0;

ISR(TIMER1_COMPA_vect) {
    isMotorUpgarad = 1;

    if (ledTestFlag == 0) {
        ledTestFlag = 1;
        digitalWrite(13, HIGH);
    }
    else {
        ledTestFlag = 0;
        digitalWrite(13, LOW);
    }
}

// Set the motor to the frame
void SetFrameRun(uint16_t frame, uint16_t delayms) {
    if (frame >= MOTOR_FRAME_MAX) {
        return;
    }

#define MOTOR_RESEND_TIME 20

    if (delayms <= MOTOR_RESEND_TIME) {
        UART_Send_FrameByRom(&motor_para[frame][0][0]);

        busy_delay(delayms);
    }
    else {
        do {
            UART_Send_FrameByRom(&motor_para[frame][0][0]);
            busy_delay(MOTOR_RESEND_TIME);
            delayms -= MOTOR_RESEND_TIME;
        } while (delayms >= MOTOR_RESEND_TIME);
        busy_delay(delayms);
    }
}

/******************************************
 *        Motor Adjust parameter          *
 ******************************************/
#define UART_CMD_ACK "MCMA"
#define UART_CMD_ACK_SET_END (strlen(UART_CMD_ACK))  // 4 byte

#define UART_CMD_DUMMY_POWER "MDYP"
#define UART_CMD_DUMMY_POWER_IDX (strlen(UART_CMD_DUMMY_POWER))  // 4 byte
#define UART_CMD_DUMMY_POWER_IDX_CNT (1)
#define UART_CMD_DUMMY_POWER_ID \
    (UART_CMD_DUMMY_POWER_IDX + UART_CMD_DUMMY_POWER_IDX_CNT)  // 2 byte
#define UART_CMD_DUMMY_POWER_ID_CNT (2)
#define UART_CMD_DUMMY_POWER_ENABLE \
    (UART_CMD_DUMMY_POWER_ID + UART_CMD_DUMMY_POWER_ID_CNT)  // 1 byte
#define UART_CMD_DUMMY_POWER_ENABLE_CNT (1)
#define UART_CMD_DUMMY_POWER_POSITION \
    (UART_CMD_DUMMY_POWER_ENABLE + UART_CMD_DUMMY_POWER_ENABLE_CNT)  // 4 byte
#define UART_CMD_DUMMY_POWER_POSITION_CNT (4)
#define UART_CMD_DUMMY_POWER_SPEED   \
    (UART_CMD_DUMMY_POWER_POSITION + \
     UART_CMD_DUMMY_POWER_POSITION_CNT)  // 4 byte
#define UART_CMD_DUMMY_POWER_SPEED_CNT (4)
#define UART_CMD_DUMMY_POWER_END \
    (UART_CMD_DUMMY_POWER_SPEED + UART_CMD_DUMMY_POWER_SPEED_CNT)

#define UART_CMD_DUMMY_DATA "MDYD"
#define UART_CMD_DUMMY_DATA_IDX (strlen(UART_CMD_DUMMY_DATA))  // 4 byte
#define UART_CMD_DUMMY_DATA_IDX_CNT (1)
#define UART_CMD_DUMMY_DATA_ID \
    (UART_CMD_DUMMY_DATA_IDX + UART_CMD_DUMMY_DATA_IDX_CNT)  // 2 byte
#define UART_CMD_DUMMY_DATA_ID_CNT (2)
#define UART_CMD_DUMMY_DATA_END \
    (UART_CMD_DUMMY_DATA_ID + UART_CMD_DUMMY_DATA_ID_CNT)

#define UART_CMD_SENSOR "MCMS"
#define UART_CMD_SENSOR_IDX (strlen(UART_CMD_SENSOR))  // 4 byte
#define UART_CMD_SENSOR_IDX_CNT (1)
#define UART_CMD_SENSOR_ID \
    (UART_CMD_SENSOR_IDX + UART_CMD_SENSOR_IDX_CNT)  // 2 byte
#define UART_CMD_SENSOR_ID_CNT (2)
#define UART_CMD_SENSOR_ENABLE \
    (UART_CMD_SENSOR_ID + UART_CMD_SENSOR_ID_CNT)  // 1 byte
#define UART_CMD_SENSOR_ENABLE_CNT (1)
#define UART_CMD_SENSOR_SET_END \
    (UART_CMD_SENSOR_ENABLE + UART_CMD_SENSOR_ENABLE_CNT)

#define UART_CMD_BEGIN "MCMB"
#define UART_CMD_BEGIN_SET_MAX (strlen(UART_CMD_BEGIN))  // 4 byte
#define UART_CMD_BEGIN_SET_MAX_CNT (4)
#define UART_CMD_BEGIN_SET_MIN \
    (UART_CMD_BEGIN_SET_MAX + UART_CMD_BEGIN_SET_MAX_CNT)  // 4 byte
#define UART_CMD_BEGIN_SET_MIN_CNT (4)
#define UART_CMD_BEGIN_SET_END \
    (UART_CMD_BEGIN_SET_MIN + UART_CMD_BEGIN_SET_MIN_CNT)

#define UART_CMD_MOTORSET "MS"
#define UART_CMD_SET_CMDIDX_IDX (strlen(UART_CMD_MOTORSET))  // 1 byte
#define UART_CMD_SET_CMDIDX_IDX_CNT (1)
#define UART_CMD_SET_CHA_IDX \
    (UART_CMD_SET_CMDIDX_IDX + UART_CMD_SET_CMDIDX_IDX_CNT)  // 2 byte
#define UART_CMD_SET_CHA_IDX_CNT (2)
#define UART_CMD_SET_EN_IDX \
    (UART_CMD_SET_CHA_IDX + UART_CMD_SET_CHA_IDX_CNT)  // 1 byte
#define UART_CMD_SET_EN_IDX_CNT (1)
#define UART_CMD_SET_POS_IDX \
    (UART_CMD_SET_EN_IDX + UART_CMD_SET_EN_IDX_CNT)  // 4 bytes
#define UART_CMD_SET_POS_IDX_CNT (4)
#define UART_CMD_SET_TIME_IDX \
    (UART_CMD_SET_POS_IDX + UART_CMD_SET_POS_IDX_CNT)  // 5 bytes
#define UART_CMD_SET_TIME_IDX_CNT (5)
#define UART_CMD_SET_END_IDX \
    (UART_CMD_SET_TIME_IDX + UART_CMD_SET_TIME_IDX_CNT)  // 1 bytes
#define UART_CMD_SET_END_IDX_CNT (1)
#define UART_CMD_SET_END (UART_CMD_SET_END_IDX + UART_CMD_SET_END_IDX_CNT)  //
// Check if the usb is connected
int16_t uart_isConnectToPC() {
    if (uart_getCmd() == 0) {
        uart_checkCmd();

        return uart_isUartMode;
    }
    return 0;
}

void uart_clearCmdBuf() {
    memset(uart_CmdBuf, 0x00, UART_CMDBUF_MAX);
    uart_CmdBufIdx = 0;
}

int16_t uart_getCmd() {
    while (Serial.available()) {
        uart_CmdBuf[uart_CmdBufIdx] = Serial.read();
        if (++uart_CmdBufIdx >= UART_CMDBUF_MAX) {
            uart_clearCmdBuf();
        }
        return 0;
    }

    return -1;
}

int16_t uart_cmdBegin() {
    uint8_t* targetStr;
    if ((targetStr = (uint8_t*)strstr((char*)uart_CmdBuf, UART_CMD_BEGIN)) !=
        0) {
        uint16_t tmpMax, tmpMin;
        tmpMax = strToInt(targetStr + UART_CMD_BEGIN_SET_MAX,
                          UART_CMD_BEGIN_SET_MAX_CNT);
        tmpMin = strToInt(targetStr + UART_CMD_BEGIN_SET_MIN,
                          UART_CMD_BEGIN_SET_MIN_CNT);
        if (tmpMax <= tmpMin || tmpMax > 3000 || tmpMin > 3000 || tmpMax == 0 ||
            tmpMin == 0) {
            return -3;
        }
        motorPosMax = tmpMax;
        motorPosMin = tmpMin;

        uart_clearCmdBuf();
        uart_isUartMode = 1;

        Serial.write(UART_CMD_BEGIN, strlen(UART_CMD_BEGIN));
        Serial.flush();
        return 0;
    }
    else {
        return -2;
    }
}

int16_t uart_cmdAck() {
    uint8_t* targetStr;
    if ((targetStr = (uint8_t*)strstr((char*)uart_CmdBuf, UART_CMD_ACK)) != 0) {
        uart_clearCmdBuf();

        Serial.write(UART_CMD_ACK, strlen(UART_CMD_ACK));
        Serial.flush();
        return 0;
    }
    else {
        return -2;
    }
}

int16_t uart_cmdMotor() {
    uint8_t* targetStr;
    if ((targetStr = (uint8_t*)strstr((char*)uart_CmdBuf, UART_CMD_MOTORSET)) !=
        0) {
        uart_cmdIdx = strToInt(targetStr + UART_CMD_SET_CMDIDX_IDX,
                               UART_CMD_SET_CMDIDX_IDX_CNT);

        uart_cmdChannel = strToInt(targetStr + UART_CMD_SET_CHA_IDX,
                                   UART_CMD_SET_CHA_IDX_CNT);

        uart_cmdEn =
            strToInt(targetStr + UART_CMD_SET_EN_IDX, UART_CMD_SET_EN_IDX_CNT);

        uart_cmdPos = strToInt(targetStr + UART_CMD_SET_POS_IDX,
                               UART_CMD_SET_POS_IDX_CNT);

        uart_cmdTime = strToInt(targetStr + UART_CMD_SET_TIME_IDX,
                                UART_CMD_SET_TIME_IDX_CNT);

        uart_clearCmdBuf();

        if (uart_cmdChannel >= MOTOR_MOTOR_MAX) {
            return -4;
        }
        if (uart_cmdEn != 0 && uart_cmdEn != 1) {
            return -5;
        }

        if (uart_cmdPos > motorPosMax || uart_cmdPos < motorPosMin) {
            return -6;
        }

        MotorPool[uart_cmdChannel][MOTOR_EN] = uart_cmdEn;
        MotorPool[uart_cmdChannel][MOTOR_POS] = uart_cmdPos;
        MotorPool[uart_cmdChannel][MOTOR_SPEED] = uart_cmdTime;

        return 0;
    }
    else {
        return -7;
    }
}

int16_t uart_cmdDummyMotorPower() {
    uint8_t* targetStr;
    uint16_t uart_cmdPos;
    uint16_t uart_cmdSpeed;

    if ((targetStr =
             (uint8_t*)strstr((char*)uart_CmdBuf, UART_CMD_DUMMY_POWER)) != 0) {
        uart_cmdIdx = strToInt(targetStr + UART_CMD_DUMMY_POWER_IDX,
                               UART_CMD_DUMMY_POWER_IDX_CNT);

        uart_cmdMotorId = strToInt(targetStr + UART_CMD_DUMMY_POWER_ID,
                                   UART_CMD_DUMMY_POWER_ID_CNT);

        uart_cmdEn = strToInt(targetStr + UART_CMD_DUMMY_POWER_ENABLE,
                              UART_CMD_DUMMY_POWER_ENABLE_CNT);

        uart_cmdPos = strToInt(targetStr + UART_CMD_DUMMY_POWER_POSITION,
                               UART_CMD_DUMMY_POWER_POSITION_CNT);

        uart_cmdSpeed = strToInt(targetStr + UART_CMD_DUMMY_POWER_SPEED,
                                 UART_CMD_DUMMY_POWER_SPEED_CNT);

        uart_clearCmdBuf();

        if (uart_cmdMotorId > MOTOR_MOTOR_MAX) {
            return -4;
        }
        if (uart_cmdEn != 0 && uart_cmdEn != 1) {
            return -5;
        }

        while (Serial1.available()) {
            Serial1.read();
        }

        if (uart_cmdEn == 1) {
            UART_Send_SetMotorPosition(uart_cmdMotorId, uart_cmdPos,
                                       uart_cmdSpeed);
        }
        else {
            UART_Send_SetMotorPosition(uart_cmdMotorId, 0, 0);
        }

        uint8_t tmpBuf[16] = {0x00};
        snprintf((char*)tmpBuf, sizeof(tmpBuf), "%s", UART_CMD_DUMMY_POWER);
        Serial.write((const char*)tmpBuf, strlen((const char*)tmpBuf));
        Serial.flush();

        return 0;
    }
    else {
        return -7;
    }
}

int16_t uart_cmdDummyMotorPosition() {
    uint8_t* targetStr;
    uint8_t tmp_motorId;

    if ((targetStr =
             (uint8_t*)strstr((char*)uart_CmdBuf, UART_CMD_DUMMY_DATA)) != 0) {
        uart_cmdIdx = strToInt(targetStr + UART_CMD_DUMMY_DATA_IDX,
                               UART_CMD_DUMMY_DATA_IDX_CNT);

        tmp_motorId = strToInt(targetStr + UART_CMD_DUMMY_DATA_ID,
                               UART_CMD_DUMMY_DATA_ID_CNT);

        uart_clearCmdBuf();

        if (tmp_motorId > MOTOR_MOTOR_MAX) {
            return -4;
        }

        if (tmp_motorId != uart_cmdMotorId) {
            return -5;
        }

        UART_Send_SetMotorPosition(tmp_motorId, 0, 0);

        delay(5);

        while (Serial1.available()) {
            Serial1.read();
        }

        UART_Send_GetMotorPosiiton(uart_cmdMotorId);

#define UART_MOTORBUG_MAX 32
#define UART_MOTOR_POS_RET_LEN 11

        uint8_t tmp_GetUartBuf[UART_MOTORBUG_MAX] = {0};
        uint16_t tmp_GetUartBufIdx = 0;

        for (uint8_t ii = 0; ii < 5; ii++) {
            while (Serial1.available()) {
                tmp_GetUartBuf[tmp_GetUartBufIdx++] = Serial1.read();
            }
            if (tmp_GetUartBufIdx >= UART_MOTORBUG_MAX) {
                break;
            }
            delay(1);
        }

        if (tmp_GetUartBufIdx < UART_MOTOR_POS_RET_LEN) {
            return -8;
        }

        for (uint8_t ii = 0; ii < tmp_GetUartBufIdx; ii++) {
            if (tmp_GetUartBuf[ii] == (0x80 + uart_cmdMotorId) &&
                tmp_GetUartBuf[ii + 1] == 0x91 &&
                tmp_GetUartBuf[ii + 2] == 0x03) {
                uint16_t tmp_pos = (uint16_t)tmp_GetUartBuf[ii + 3] * 256 +
                                   (uint16_t)tmp_GetUartBuf[ii + 4];

                uint8_t tmpBuf[16] = {0x00};
                snprintf((char*)tmpBuf, sizeof(tmpBuf), "%s%04d",
                         UART_CMD_DUMMY_DATA, tmp_pos);
                Serial.write((const char*)tmpBuf, strlen((const char*)tmpBuf));
                Serial.flush();

                break;
            }
        }

        return 0;
    }
    else {
        return -7;
    }
}

int16_t uart_checkCmd() {
    if (uart_isUartMode == 0) {
        if (strlen((char*)uart_CmdBuf) < UART_CMD_BEGIN_SET_END) {
            return -1;
        }
        return uart_cmdBegin();
    }
    else {
        int retValue = 0;

        if (strlen((char*)uart_CmdBuf) >= UART_CMD_ACK_SET_END) {
            retValue = uart_cmdAck();
            if (retValue == 0) {
                return retValue;
            }
        }
        if (strlen((char*)uart_CmdBuf) >= UART_CMD_BEGIN_SET_END) {
            retValue = uart_cmdBegin();
            if (retValue == 0) {
                return retValue;
            }
        }

        if (strlen((const char*)uart_CmdBuf) >= UART_CMD_SET_END) {
            retValue = uart_cmdMotor();
            if (retValue == 0) {
                return retValue;
            }
        }

        if (strlen((const char*)uart_CmdBuf) >= UART_CMD_DUMMY_POWER_END) {
            retValue = uart_cmdDummyMotorPower();
            if (retValue == 0) {
                return 1;
            }
        }

        if (strlen((const char*)uart_CmdBuf) >= UART_CMD_DUMMY_DATA_END) {
            retValue = uart_cmdDummyMotorPosition();
            if (retValue == 0) {
                return 1;
            }
        }

        return -3;
    }
    return -1;
}

uint16_t strToInt(uint8_t* str, uint8_t len) {
    uint16_t tmp = 0;

    for (uint8_t ii = 0; ii < len; ii++) {
        tmp *= 10;
        tmp += (*(str + ii) - '0');
    }

    return tmp;
}

/******************************************
 *        Robot action functon            *
 ******************************************/

uint16_t uart_disableMotor() {
    memset(&MotorPool[0][0], 0x00, sizeof(MotorPool));
    UART_Send_Frame(&MotorPool[0][0]);
    Serial1.flush();
    busy_delay(100);
}

uint16_t uart_firstStartMotor() {
    memset(&MotorPool[0][0], 0x00, sizeof(MotorPool));

    for (uint8_t ii = 0; ii < MOTOR_MOTOR_MAX; ii++) {
        MotorPool[ii][MOTOR_EN] = 1;
        MotorPool[ii][MOTOR_POS] = 1500;
        MotorPool[ii][MOTOR_SPEED] = 1000;
    }

    UART_Send_Frame(&MotorPool[0][0]);
    Serial1.flush();
    busy_delay(1500);

    memset(&MotorPool[0][0], 0x00, sizeof(MotorPool));
}

void UART_Send_Frame(uint16_t* FrameData) {
    uint16_t pos = 0;
    uint16_t time = 0;

    Checksum_Calc = 0;
    UART_Send_MotionHeader();
    uint8_t ii;
    for (ii = 0; ii < 32; ii++) {
        if (ii >= MOTOR_MOTOR_MAX) {
            pos = 0;
            time = 0;
        }
        else {
            if (*(FrameData + ii * MOTOR_PARA_MAX + MOTOR_EN) == 0) {
                pos = 0;
                time = 0;
            }
            else {
                pos = *(FrameData + ii * MOTOR_PARA_MAX + MOTOR_POS);
                time = *(FrameData + ii * MOTOR_PARA_MAX + MOTOR_SPEED);
            }
        }

        UART_Send_PosAndTime(ii + 1, pos, time);
    }

    UART_Send_Checksum();
    Serial1.flush();
}

// void UART_Send_FrameByRom( uint16_t * FrameData, uint16_t frame = 0xFF ) // This format of function able to get frame number before sending data to motor
void UART_Send_FrameByRom(uint16_t* FrameData) {
    uint16_t pos = 0;
    uint16_t time = 0;

    Checksum_Calc = 0;
    UART_Send_MotionHeader();
    uint8_t ii;
    for (ii = 0; ii < 32; ii++) {
        if (ii >= MOTOR_MOTOR_MAX) {
            pos = 0;
            time = 0;
        }
        else {
            if (pgm_read_word_near(FrameData + ii * MOTOR_PARA_MAX +
                                   MOTOR_EN) == 0) {
                pos = 0;
                time = 0;
            }
            else {
                pos = pgm_read_word_near(FrameData + ii * MOTOR_PARA_MAX +
                                         MOTOR_POS);
                time = pgm_read_word_near(FrameData + ii * MOTOR_PARA_MAX +
                                          MOTOR_SPEED);
            }
        }
        UART_Send_PosAndTime(ii + 1, pos, time);
    }
    UART_Send_Checksum();
    Serial1.flush();
}

void UART_Send_MotionHeader(void) {
    UART_Send(0x80 | 0x00);  // header mark & broadcast ID
    UART_Send(0x80 | 0x82);  // header mark & commaand code
    UART_Send(0xA2);         // total data length
    UART_Send(0x05);         // data length (one servo with time and speed)
}

void UART_Send_PosAndTime(uint8_t ID, uint16_t Position, uint16_t Time) {
    UART_Send(ID);                       // ServoID
    UART_Send((Position / 256) & 0x7F);  // Servo Pos_H
    UART_Send(Position % 256);           // Servo Pos_L
    UART_Send((Time / 256) & 0x7F);      // Servo Time_H
    UART_Send(Time % 256);               // Servo Time_L
}

void UART_Send_Checksum() {
    Serial1.write(Checksum_Calc);
    Serial1.write(0xff);

    Checksum_Calc = 0;
}

void UART_Send(uint8_t u8_byte_data) {
    Serial1.write(u8_byte_data);
    Checksum_Calc += u8_byte_data;
}

void UART_Send_SetMotorPosition(uint16_t motorId, uint16_t Postion,
                                uint16_t Time) {
    Checksum_Calc = 0;
    UART_Send(0x80 + motorId);          // header mark & broadcast ID
    UART_Send(0x83);                    // header mark & commaand code
    UART_Send(0x05);                    // total data length
    UART_Send((Postion / 256) & 0x7F);  // Servo Pos_H
    UART_Send(Postion % 256);           // Servo Pos_L
    UART_Send((Time / 256) & 0x7F);     // Servo Time_H
    UART_Send(Time % 256);              // Servo Time_L
    UART_Send(Checksum_Calc);  // data length (one servo with time and speed)
}

void UART_Send_GetMotorPosiiton(uint16_t motorId) {
    Checksum_Calc = 0;
    UART_Send(0x80 + motorId);  // header mark & broadcast ID
    UART_Send(0x91);            // header mark & commaand code
    UART_Send(0x01);            // return data length
    UART_Send(0x05);            // start address
    UART_Send(Checksum_Calc);   // data length (one servo with time and speed)
}

bool isCmd(char comp) {
    for (int i = 0; i < sizeof(cmd_list); i++) {
        if (comp == cmd_list[i]) return true;
    }
    return false;
}

// Used to get data while delaying, and store into buffer
// @param limit => The delay time
// @param interupt => If we want the delay to stop after getting '$'
void busy_delay(uint16_t limit, bool interupt = false) {
    if (limit > 0) {
        uint64_t tic = millis();

        while (millis() - tic <
               (uint64_t)limit) {  // When the delay is not done yet

            // If it's not fell and not defensing
            if (started && !getup_flag && cmd != CMD_F_DEFENSE &&
                cmd != CMD_L_DEFENSE && cmd != CMD_R_DEFENSE) {
                checkAcce();
            }

            // Recieve data while delaying
            if (RFSerial.available()) {
                char tmp = RFSerial.read();
                Serial.println(tmp);
                // If the data is in the range
                if (isCmd(tmp) || (tmp > '0' && tmp <= '9') || tmp == '#' || tmp == '$') {
//                if ( (tmp > '0' && tmp <= '9') || tmp == '#' || tmp == '$') {
                    if (tmp == '#') {
                        rcev_buf_count = 0;
                        memset(rcev_buf, 0x00, sizeof(rcev_buf));
                    }
                    else
                        rcev_buf_count++;

                    if (rcev_buf_count >= rcev_buf_size) rcev_buf_count = 0;

                    rcev_buf[rcev_buf_count] = tmp;

                    if (tmp == '$' && interupt) return;
                }
            }
        }
    }
}
