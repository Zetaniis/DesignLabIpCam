#include <Servo.h>
int data = 0;           
char userInput;

int servoVertPin = 9;
int servoHorPin = 11;

int servoPin = 9;
Servo servoVert, servoHor;  
int servoAngle = 0; 
char buff[2] = {0,0};
void setup(){

  Serial.begin(9600);            //  setup serial
  servoVert.attach(servoVertPin);
  servoHor.attach(servoHorPin);
}

void loop(){

if(Serial.available()> 0){ 
    userInput = Serial.read();               // read user input 
    if (userInput=='1'){
      servoVert.write(79);
      delay(50);
      servoHor.write(97.5);
      delay(50);
    }
    else if (userInput=='2'){
      servoVert.write(79);
      delay(50);
      servoHor.write(87);
      delay(50);
    }
    else if (userInput=='3'){
      servoVert.write(79);
      delay(50);
      servoHor.write(72);
      delay(50);
    }
    else if (userInput=='4'){
      servoVert.write(89);
      delay(50);
      servoHor.write(97.5);
      delay(50);
    }
    else if (userInput=='5'){
      servoVert.write(89);
      delay(50);
      servoHor.write(87.5);
      delay(50);
    }
    else if (userInput=='6'){
      servoVert.write(89);
      delay(50);
      servoHor.write(72);
      delay(50);
    }
    else if (userInput=='7'){
      servoVert.write(95);
      delay(50);
      servoHor.write(97.5);
      delay(50);
    }
    else if (userInput=='8'){
      servoVert.write(95);
      delay(50);
      servoHor.write(87);
      delay(50);
    }
    else if (userInput=='9'){
      servoVert.write(95);
      delay(50);
      servoHor.write(72);
      delay(50);
    }
    else {
      servoVert.write(89);
      delay(50);
      servoHor.write(87.5);
      delay(50);
    }
    
    //delay(100);
      
   } // Serial.available
   else {
    servoVert.write(89);
    servoHor.write(87.5);
   }

} // Void Loop
