#include <SPI.h>

#ifndef cbi
#define cbi(sfr, bit) (_SFR_BYTE(sfr) &= ~_BV(bit))
#endif
#ifndef sbi
#define sbi(sfr, bit) (_SFR_BYTE(sfr) |= _BV(bit))
#endif

int outputVoltage = 128;
int voltageArray[256];
long analogArray[256];
int addr = 0;
long markerTime;
long timeStamp = 0;
long result;

const byte CS = 10;  // digital pin 10 for /CS

void setup() {
  Serial.begin(9600);
  pinMode(CS,OUTPUT);
  cbi(PORTB,2);
  
  SPI.begin();
  SPI.setBitOrder(MSBFIRST);
  SPI.setDataMode(SPI_MODE1);
  SPI.setClockDivider(SPI_CLOCK_DIV2);
  
  DDRD = 0xFF;
  for (int j=0 ; j<5 ; j++) {
    if (j==0 | j>2) {
      markerTime = micros();
      rampDown();
      rampUp();
      serPrint();
      markerTime = micros();
      zeroRamp();
      serPrint();
    }
    else {
      markerTime = micros();
      rampUp();
      rampDown();
      serPrint();
      markerTime = micros();
      zeroRamp();
      serPrint();
    }
    addr=0;
  }
}
  
void loop() {
}

void rampUp() {
  for (int i=0 ; i<127 ; i++) {
    outputVoltage++;
    measure();
  }
}

void rampDown() {
  for (int i=0 ; i<127 ; i++) {
    outputVoltage--;
    measure();
  }
}

void zeroRamp() {
  for (int i=0 ; i<254 ; i++) {
    measure();
  }
}

void measure() {
  PORTD = outputVoltage;
  analogArray[addr] = SpiRead();
  voltageArray[addr] = outputVoltage;
  addr++;
}

void serPrint() {
  timeStamp = micros()-markerTime;
  Serial.println(timeStamp);
  for (int i=0 ; i<252 ; i++) {
    Serial.println(voltageArray[i]);
    Serial.println(analogArray[i]);
  }
  addr = 0;
}

long SpiRead(void) {
  cbi(PORTB,2);
  
  result = SPI.transfer(0xFF)<<8 | SPI.transfer(0xFF) >>2;
  
  sbi(PORTB,2);
  return(result);  
}
