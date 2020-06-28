/*
custom.ino

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

#include "acceler.h"
#include "action.h"
#include "custom.h"

bool damping = 0;

void custom_setup() {
    acce_init(PP_SENSOR_TYPE_ACCELER);
    rf24_init(PP_SENSOR_TYPE_RF24KEY);
    cmdSetup();
}

void custom_loop() {
    char rf24_key;

    uart_disableMotor();
    memset(rcev_buf, 0, sizeof(rcev_buf));

    // wait the time to start machine
    while (millis() - init_tic < START_DELAY) {
//        memset(rcev_buf, 0, sizeof(rcev_buf));

        if (uart_isConnectToPC() != 0) return;

        rf24_key = getData();
//        Serial.print("started   ");
//        Serial.print(started);
//        Serial.print("  get key   ");
//        Serial.println(rf24_key);
        if ((rf24_key = getData()) == CMD_START) {
            break;
        }
    }

    Serial.println("START KEY");
    uart_firstStartMotor();
    SetFrameRun(1, 200);
    started = 1;
    //      SetFrameRun(88, 1500);

    while (uart_isUartMode == 0) {
        if (uart_isConnectToPC() != 0) return;
        if (started && !PK_MODE) {
            rf24_sendAck();
        }
        //    cmd = getData();
        doAction();

    }
}

void checkAcce() {
    uint16_t tmp = millis() - acc_tic;
    if( millis() - acc_tic < ACC_DELAY ){
        if ( tmp > 10*status_count[TOTAL] ) {
            check_body_status();
#ifdef CHECK_ACC
            Serial.println("");
#endif
        }
    }
    else {
        // Find Maximum index
        uint16_t max_index = 0;
        for(int i = 1; i < TOTAL; i++) {
            if(status_count[max_index] < status_count[i] ) {
                status_count[max_index] = 0;
                max_index = i;
            }
            else
                status_count[i] = 0;
        }
        status_count[max_index] = 0;
        status_count[TOTAL] = 0;

        // Decide to getup
        getUp(max_index);
        
        acc_tic = millis();
    }
    //  accAdj();
}

void cmdSetup() {
    //  while(true) {
    //    Serial.println( analogRead(CMD_PIN) );
    //  }
    uint16_t reading = analogRead(CMD_PIN);
    //  delay(2000);
    //  Serial.println(reading);
    if (reading < 341)
        CMD_ID = 1;
    else if (reading > 900)
        CMD_ID = 2;
    else
        CMD_ID = 0;
}
