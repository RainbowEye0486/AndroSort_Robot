/*
rf24.ino
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
//*/
#include "rf24.h"

uint8_t key = 0;

int16_t rf24_init(uint8_t id) {
    //  Serial.println("rf24_init");
    if (id == PP_SENSOR_TYPE_RF24KEY) {
        pp_sensor[id].isEnable = 1;
        rf24_enable(id);
        return 0;
    }
    return -1;
}

int16_t rf24_enable(uint8_t id) {
    //    Serial.println("rf24_enable");
    RF24.setTxAdd(addr[0], sizeof(addr[0]));
    delay(150);
    RF24.setRxAdd(addr[1], sizeof(addr[1]));
    delay(150);
    RF24.setFreq(FREQ);
    delay(150);
    RF24.setComRate(SEND_RATE);
    delay(150);
    RF24.setCRC(CRC);
    delay(150);

//    if (RF24.kick()) Serial.println("ready");

    key = 0;
    move_num = 0;
}

// bool flush_rx_flag = 1;
// uint8_t key = 0;
int8_t rf24_getData(uint8_t id) {
    if (id != PP_SENSOR_TYPE_RF24KEY) {
        return 0;
    }
    if (started && !PK_MODE) {
        checkAcce();
    }

//    Serial.println(move_num);
    
//    memset(rcev_buf, 0x00, sizeof(rcev_buf));
    if (PK_MODE)
        busy_delay(130, true);
    else
        busy_delay(130);
    if (move_num == 0 || rcev_buf[0] != 0) {
        key = 0;
        //    uint8_t buffer[31] = {};
        //    RF24.recv(buffer, sizeof(buffer), 30);

#ifndef CHECK_ACC
        for (int i = 0; i < sizeof(rcev_buf); i++)
            Serial.print((char)rcev_buf[i]);
        Serial.println("");
#endif

        if (rcev_buf[0] == '#' && rcev_buf[7] == '$') {
            key = rcev_buf[CMD_ID * 2 + 1];
            move_num = rcev_buf[CMD_ID * 2 + 2] - 48;
            memset(rcev_buf, 0x00, sizeof(rcev_buf));

#ifndef CHECK_ACC
            Serial.print(move_num);
            Serial.print("In wifi.c, get key: ");
            Serial.println((char)key);
#endif
        }
    }

    if (move_num > 0) move_num--;

    return key;
}

void rf24_sendAck() {
    uint8_t getKeyCmd[5] = {};

    // Send acknowledge back every one sec
    if (millis() - ack_tic > ack_time_delay) {
        if (!isCmd(key))
            sprintf(getKeyCmd, "#%d%d$", CMD_ID, started);
        else
            sprintf(getKeyCmd, "#%d%c$", CMD_ID, key);

#ifndef CHECK_ACC
        Serial.print("send ack:");
        for (int i = 0; i < 4; i++) {
            Serial.print((char)getKeyCmd[i]);
        }
        Serial.println("");
#endif

        RF24.send(getKeyCmd, sizeof(getKeyCmd));
        ack_tic = millis();
    }
}
