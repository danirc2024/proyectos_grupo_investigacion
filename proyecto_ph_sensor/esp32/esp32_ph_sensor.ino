#include <OneWire.h>
#include <DallasTemperature.h>
#define nRx 23
#define nTx 22
#define nID 1 
const byte aCMD[] = {0x01,0x03,0x00,0x09,0x00,0x01,0x54,0x08};
const byte nGPTE = 27; 
byte aData[7]; 
float fPH, fTE;
OneWire oneWire(nGPTE);          
DallasTemperature st(&oneWire);  
HardwareSerial PHS(2); 
void setup()
  {
    Serial.begin(9600);
    PHS.begin(9600, SERIAL_8N1, nRx, nTx); 
    st.begin();
    delay(3000);
  }
void loop()
  {
    PHS.flush();
    if (PHS.write(aCMD, sizeof(aCMD)) == 8)
      {
        PHS.readBytes(aData, 7);
      }
    
    fPH = aData[4] / 10.0; 
    Serial.print("Soil PH: "); 
    Serial.println(fPH, 1);
    
    st.requestTemperatures(); 
    fTE = st.getTempCByIndex(0);
    Serial.print("Temperatura: ");
    Serial.print(fTE); 
    Serial.println(" °C");
    
    delay(10000);
  }