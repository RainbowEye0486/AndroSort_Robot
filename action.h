/*
action.h
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

#ifndef __ACTION_H__
#define __ACTION_H__

// Falling prevention var
short pos_delay_count = 1;
short pos_delay_set = 0;


//#define ERROR_COUNT 5

char cmd_list[] = {'z', 'x', 'c', 'w', 's', 'a', 'd', 'q', 'e', 'W',
                   'A', 'D', 'Q', 'E', 'p', 'o', 'i', 'u', 'j', 'h',
                   'n', 'b', 'y', 'Y', 'g', 'f', 'G', 'F', 'r', 'R','N'/*,'l*/};

enum {
    CMD_START = 'z',
    CMD_STOP = 'x',
    CMD_PK = 'c',

    // Normal moving
    CMD_FORWARD = 'w',
    CMD_BACKWARD = 's',
    CMD_TRUN_LEFT = 'q',
    CMD_TRUN_RIGHT = 'e',
    CMD_MOVE_LEFT = 'a',
    CMD_MOVE_RIGHT = 'd',

    // F for fast, fast moving
    CMD_FFORWARD = 'W',
    CMD_FMOVE_LEFT = 'A',
    CMD_FMOVE_RIGHT = 'D',
    CMD_FTRUN_LEFT = 'Q',
    CMD_FTRUN_RIGHT = 'E',

    // Kick command, pass or all direction pass
    CMD_RPASS = 'p',
    CMD_LPASS = 'o',
    CMD_RFSHOOT = 'i',  // Right forward shoot
    CMD_LFSHOOT = 'u',  // Left forward shoot
    CMD_RSSHOOT = 'j',  // Right side shoot
    CMD_LSSHOOT = 'h',  // Left side shoot
    CMD_RBSHOOT = 'n',  // Right backward shoot
    CMD_LBSHOOT = 'b',  // Left backward shoot

    // Defence
    CMD_DEFENSE = 'y',
    CMD_F_DEFENSE = 'Y',
    CMD_R_DEFENSE = 'g',
    CMD_L_DEFENSE = 'f',
    //CMD_SPLIT ='l',

    /* low move
    CMD_R_DEFENSE = 'G',
    CMD_L_DEFENSE = 'F',
    CMD_R_LOW = 'g',
    CMD_L_LOW = 'f',
    */

    CMD_REST = 'r',
    CMD_STAND = 'R',
};

uint8_t cmd;

void doAction();
void indAction();
uint8_t getData();
void getUp(uint16_t body_status);
void steady();

void R1Action();
void R2Action();
void R3Action();
void R4Action();
void R5Action();
void R6Action();
void R7Action();

#endif  // __ACTION_H__
