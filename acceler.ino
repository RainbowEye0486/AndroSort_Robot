/*
acceler.ino
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

// For GY-61  (ADXL335)

//int acc_offset[] = {512, 512, 512};

int16_t acce_init(uint8_t id) {
  if (id == PP_SENSOR_TYPE_ACCELER) {
    pp_sensor[id].isEnable = 1;
    acce_enable(id);
  }

  return 0;
}

int16_t acce_enable(uint8_t id) {
  analogReference(EXTERNAL);

  return 0;
}

int16_t acce_disable(uint8_t id) { return 0; }

int16_t acce_getDirValue(uint8_t id, uint8_t dir) {
  if (id == PP_SENSOR_TYPE_ACCELER && pp_sensor[id].isEnable == 1) {
    int16_t tmp = 0;
    switch (dir) {
      case ACCE_DIR_X:
        tmp = analogRead(ACCE_X_PIN);
#ifdef CHECK_ACC
//        Serial.print("ACC_X =");
        Serial.print(tmp);
#endif
        //        return analogRead(ACCE_X_PIN) - 512;
        return tmp - acc_offset[0];
        break;

      case ACCE_DIR_Y:
        tmp = analogRead(ACCE_Y_PIN);
#ifdef CHECK_ACC
//        Serial.print("ACC_Y =");
        Serial.print(tmp);
#endif
        //        return analogRead(ACCE_Y_PIN) - 512;
        return tmp - acc_offset[1];
        break;

      case ACCE_DIR_Z:
        tmp = analogRead(ACCE_Z_PIN);
#ifdef CHECK_ACC
//        Serial.print("ACC_Z =");
        Serial.print(tmp);
#endif
        //        return analogRead(ACCE_Z_PIN) - 512;
        return tmp - acc_offset[2];
        break;
    }
  }
  return -1;
}

void check_body_status() {
    int16_t acce_x = Acce_x;
    int16_t acce_y = Acce_y;
    int16_t acce_z = Acce_z;
//    uint16_t robo_status = 0;

    status_count[TOTAL]++;
    if( abs(acce_x) < STAND_THRES && abs(acce_y) < STAND_THRES && abs(acce_z) < STAND_THRES) {
        status_count[STAND]++;
//        robo_status = STAND;
    }
    else if ( abs(acce_x) < STAND_THRES && acce_y > 70 && acce_y < 120 && acce_z >70) {
        status_count[FALL_FORWARD]++;
//        robo_status = FALL_FORWARD;
    }
    else if ( abs(acce_x) < STAND_THRES && acce_y > 70 && acce_y < 120 && acce_z < -70) {
        status_count[FALL_BACK]++;
//        robo_status = FALL_BACK;
    }
    else if (acce_x > 70 && acce_y > 70 && acce_y < 120 && abs(acce_z) < STAND_THRES) {
        status_count[FALL_LEFT]++;
//        robo_status = FALL_LEFT;
    }
    else if (acce_x < -70 && acce_y > 70 && acce_y < 120 && abs(acce_z) < STAND_THRES) {
        status_count[FALL_RIGHT]++;
//        robo_status = FALL_RIGHT;
    }
    else {              // If can't judge, defined as standing
        status_count[STAND]++;
//        robo_status = STAND;
    }
//    return robo_status;
}
