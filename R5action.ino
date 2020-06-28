/*
R7action.ino
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

void R5Action() {
    switch (cmd) {
      /*
       case CMD_SPLIT:{
        do{
          SetFrameRun(98,2000);
          SetFrameRun(97,1000);
        }while ((cmd = getData()) == CMD_SPLIT);
          
          SetFrameRun(1, 300);
        pos_delay_count = pos_delay_set;
        
        }break;
    */
          
     
       case CMD_FORWARD: {
            uint8_t jumpFlag = 0;
            SetFrameRun(0, 150);
            SetFrameRun(2, 50);//重心偏右
            do {
                SetFrameRun(3, 50);//抬左
                SetFrameRun(4, 40);//踩左
                //SetFrameRun(99,10);//重心偏左

                if ((cmd = getData()) != CMD_FORWARD) {
                    jumpFlag = 1;
                    break;
                }
                
                SetFrameRun(5, 60);//抬右
                SetFrameRun(6, 50);//踩右
                SetFrameRun(0,10);
            } while ((cmd = getData()) == CMD_FORWARD);

            if (jumpFlag == 1) {
                SetFrameRun(9, 60);//抬右多
                SetFrameRun(6, 40);//踩右
                SetFrameRun(0,10);
            }
            else {
                SetFrameRun(7, 50);//抬左多
                SetFrameRun(4, 40);//踩左
                SetFrameRun(0,10);
                SetFrameRun(99,10);
            }

            SetFrameRun(1, 500);

            pos_delay_count = pos_delay_set;
        } break;

 
        case CMD_FFORWARD: {
            uint16_t jumpFlag = 0;
            SetFrameRun(0, 150);
            SetFrameRun(2, 50);
            SetFrameRun(70, 100);//70
            SetFrameRun(71, 45);//71
            do {
                SetFrameRun(72, 200);//72
                SetFrameRun(73, 25);//73

                if ((cmd = getData()) != CMD_FFORWARD) {
                    jumpFlag = 1;
                    break;
                }

                SetFrameRun(74, 200);//74
                SetFrameRun(75, 25);//75
            } while ((cmd = getData()) == CMD_FFORWARD);

            SetFrameRun(1, 100);
            pos_delay_count = pos_delay_set;
        } break;

  /*      case CMD_BACKWARD: {
            uint8_t jumpFlag = 0;

            SetFrameRun(0, 150);
            SetFrameRun(2, 50);
            do {
                SetFrameRun(7, 65);//抬左多
                SetFrameRun(10, 115);//踩左後

                if ((cmd = getData()) != CMD_BACKWARD) {
                    jumpFlag = 1;
                    break;
                }
                SetFrameRun(9, 65);//抬右多
                SetFrameRun(8, 115);//踩右後
            } while ((cmd = getData()) == CMD_BACKWARD);

            if (jumpFlag == 1) {
                SetFrameRun(5, 70);//抬右
                SetFrameRun(8, 120);//踩右後
            }
            else {
                SetFrameRun(3, 70);//抬左
                SetFrameRun(10, 120);//踩左後
            }

            SetFrameRun(1, 100);
            pos_delay_count = pos_delay_set;
        } break;
        */
        case CMD_BACKWARD: {
            uint8_t jumpFlag = 0;

            SetFrameRun(0, 150);
            SetFrameRun(2, 50);
            do {
                SetFrameRun(3,50);//抬左多
                SetFrameRun(6, 50);//踩左後

                if ((cmd = getData()) != CMD_BACKWARD) {
                    jumpFlag = 1;
                    break;
                }
                SetFrameRun(5, 60);//抬右多
                SetFrameRun(4, 40);//踩右後
            } while ((cmd = getData()) == CMD_BACKWARD);

            if (jumpFlag == 1) {
                SetFrameRun(9, 60);//抬右
                SetFrameRun(4, 40);//踩右後
            }
            else {
                SetFrameRun(7, 50);//抬左
                SetFrameRun(6, 50);//踩左後
            }

            SetFrameRun(0, 50);
            SetFrameRun(1, 100);
           
            pos_delay_count = pos_delay_set;
        } break;


        case CMD_TRUN_RIGHT:
        do {
            SetFrameRun(12, 21);
            SetFrameRun(11, 75);
        } while((cmd = getData()) == CMD_TRUN_RIGHT);
        SetFrameRun(1, 10);
        pos_delay_count = pos_delay_set;
        break;

        
        case CMD_TRUN_LEFT:
        do {
            SetFrameRun(13, 26);
            SetFrameRun(11, 75);
        } while((cmd = getData()) == CMD_FTRUN_LEFT);
        SetFrameRun(1, 10);
        break;

        case CMD_FTRUN_RIGHT:
        do {
            SetFrameRun(12, 26);
            SetFrameRun(11, 75);
        } while((cmd = getData()) == CMD_FTRUN_RIGHT);
        SetFrameRun(1, 10);
        pos_delay_count = pos_delay_set;
        break;

        case CMD_FTRUN_LEFT:
        do {
            SetFrameRun(13, 30);
            SetFrameRun(11, 80);
        } while((cmd = getData()) == CMD_FTRUN_LEFT);
        SetFrameRun(1, 10);
        break;
        

        case CMD_MOVE_LEFT:
        do {
            SetFrameRun(15, 30);
            SetFrameRun(14, 70);   
        } while((cmd = getData()) == CMD_MOVE_LEFT);
        SetFrameRun(14, 150);
        SetFrameRun(1, 10); 
        pos_delay_count = pos_delay_set;
        break;

        case CMD_FMOVE_LEFT:
        do {
            SetFrameRun(17, 250);
            SetFrameRun(19, 100);
        } while((cmd = getData()) == CMD_FMOVE_LEFT);  
        SetFrameRun(19, 350);       
        SetFrameRun(1, 120);
    //      pos_delay_count = pos_delay_set;
        break;

        case CMD_MOVE_RIGHT:
        do {
            SetFrameRun(16, 30);
            SetFrameRun(14, 70);

        } while((cmd = getData()) == CMD_MOVE_RIGHT);
        SetFrameRun(14, 150);
        SetFrameRun(1, 10);
        pos_delay_count = pos_delay_set;

        break;

        case CMD_FMOVE_RIGHT:
        do {
            SetFrameRun(18, 250);
            SetFrameRun(19, 100); 
        } while((cmd = getData()) == CMD_FMOVE_RIGHT); 
        SetFrameRun(19, 350);        
        SetFrameRun(1, 120);
    //      pos_delay_count = pos_delay_set;
        
        break;

        case CMD_RFSHOOT:
        SetFrameRun(1, 150);
        do {      
            SetFrameRun(50, 300);
            SetFrameRun(69, 150);
            SetFrameRun(35, 100);  
        } while((cmd = getData()) == CMD_RFSHOOT);
        SetFrameRun(1, 150);
        pos_delay_count = pos_delay_set;
        break;

        case CMD_LFSHOOT :
            SetFrameRun(1, 150);
        do { 
            SetFrameRun(53,300);
            SetFrameRun(43, 150);
            SetFrameRun(45, 100);  
        } while((cmd = getData()) == CMD_LFSHOOT);
        SetFrameRun(1, 150);
        pos_delay_count = pos_delay_set;
        break;
        
        case CMD_LSSHOOT:
            SetFrameRun(0, 150);
            do {
            SetFrameRun(50, 200);
            SetFrameRun(51, 100);
            SetFrameRun(52, 80);
        } while((cmd = getData()) == CMD_LSSHOOT );
            SetFrameRun(1, 500);
    //          SetFrameRun(0, 150);
        break;

        case CMD_RSSHOOT :
        SetFrameRun(1, 150);
        do {
            SetFrameRun(53, 200);
            SetFrameRun(54, 100);
            SetFrameRun(55, 80);       

        } while((cmd = getData()) ==  CMD_RSSHOOT);
            SetFrameRun(1, 500);
    //       SetFrameRun(0, 150);
        pos_delay_count = pos_delay_set;
        break;
        
        case CMD_RBSHOOT:
        
        do {
            SetFrameRun(0, 100);
            SetFrameRun(50, 50);  
            SetFrameRun(66, 80);
            SetFrameRun(67, 50);
        } while((cmd = getData()) == CMD_RBSHOOT );
        SetFrameRun(1, 50);
        pos_delay_count = pos_delay_set;
        break;

        case CMD_LBSHOOT :
        
        do { 
            SetFrameRun(0, 100);
            SetFrameRun(53, 50);  
            SetFrameRun(41, 80);
            SetFrameRun(42, 50);
            
        } while((cmd = getData()) == CMD_LBSHOOT);
        SetFrameRun(1, 150);
        pos_delay_count = pos_delay_set;
        break;

        case CMD_RPASS:
        SetFrameRun(1, 150);
        do {     
            SetFrameRun(50, 300);
            SetFrameRun(39, 100);
        } while((cmd = getData()) == CMD_RPASS);
        SetFrameRun(1, 150);
        pos_delay_count = pos_delay_set;
        break;

        case CMD_LPASS:
        SetFrameRun(1, 150);
        do { 
            SetFrameRun(53,300); 
            SetFrameRun(40, 100); 
        } while((cmd = getData()) == CMD_LPASS);
        SetFrameRun(1, 150);
        pos_delay_count = pos_delay_set;
        break;


        case CMD_DEFENSE:         
        do {
            SetFrameRun(60, 1000);
        } while((cmd = getData()) ==  CMD_DEFENSE);
        SetFrameRun(1, 300);
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
        
        case CMD_REST:
        if(started){
            uart_disableMotor();
        }
        break;

        case CMD_STAND:
        SetFrameRun(1, 200);
        pos_delay_count = pos_delay_set;
        break;
    }
    //  steady();
}
