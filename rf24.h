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

#ifndef __RF24_PARA_H__
#define __RF24_PARA_H__

#include <SoftwareSerial.h>
#include "RF24_uart.h"
// for RF24 parameter

#define RF24_RX 14
#define RF24_TX 15

#define SEND_RATE 250
#define CRC 16

SoftwareSerial RFSerial(RF24_RX, RF24_TX);  // RX 、 TX
RF24_UART RF24(RFSerial, 9600);

//const char addr[2][10] = {"BBCCDDEEF0", "F6FFFFFFFF"};  // Tx, Rx

#if ADDR_MODE == 1
const char addr[2][10] = {"BBCCDDEEFF", "06FFFFFFFF"};  // Tx, Rx
#elif ADDR_MODE == 2
const char addr[2][10] = {"BBCCDDEEF0", "F6FFFFFFFF"};  // Tx, Rx
#elif ADDR_MODE == 3
const char addr[2][10] = {"B0C0D0E0F0", "F1F2F3F4F5"};  // Tx, Rx
#elif ADDR_MODE == 4
const char addr[2][10] = {"EE8FA92829", "92829AEE8F"};  // Tx, Rx
#elif ADDR_MODE == 5
const char addr[2][10] = {"EE8FA92833", "92833AEE8F"};  // Tx, Rx
#else
#endif


const float FREQ = 2.525;

uint64_t ack_tic = millis();
unsigned int ack_time_delay =
    5000;  // the time delay we want for sending acknowledge to robot

int16_t rf24_init(uint8_t id);
int16_t rf24_enable(uint8_t id);
int8_t rf24_getData(uint8_t id);
void rf24_sendAck();

#endif  // __ACCELER_H__
