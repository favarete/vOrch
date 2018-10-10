#include <ESP8266WiFi.h>
#include <Adafruit_ADS1015.h>
#include <Servo.h>

Adafruit_ADS1115 ads(0x4A);
int16_t servo_battery, board_battery;

//Pin definitions
#define D0    16
#define D1    5
#define D2    4
#define D3    0
#define D4    2
#define D5    14
#define D6    12
#define D7    13
#define D8    15

/*   
 *  CONFIG
 */

#define BATTERY_READ    D0

float drop_tolerance = 0.2;

// Servo Battery Sensor
float servo_battery_power = 7.4;
float servo_battery_divider_voltage = -1.0;
float servo_battery_source_voltage = -1.0;
String servo_battery_level = "";
int servo_battery_resistor1 = 100000;
int servo_battery_resistor2 = 56000;
int servo_battery_max_digital_value = 16000;
float servo_battery_max_divider_voltage = 3.0;

// Board Battery Sensor
float board_battery_power = 3.7;
float board_battery_divider_voltage = -1.0;
float board_battery_source_voltage = -1.0;
String board_battery_level = "";
int board_battery_resistor1 = 100000;
int board_battery_resistor2 = 220000;
int board_battery_max_digital_value = 16000;
float board_battery_max_divider_voltage = 3.0;

//Robot Identification
const char* ROBOT_ID = "01";

//WiFi Configuration
WiFiServer server(8888);
String header;
const char* ssid = "";
const char* password = "";

//Servo
Servo leftServo;
Servo rightServo;
int posLeft = 0;
int posRight = 0;

//Information
#define RED_LED_1   D6
#define RED_LED_2   D7
#define YELLOW_LED  D8

int red_led_1_state = LOW;
int red_led_2_state = LOW;
int yellow_led_state = LOW;

unsigned long interval=100;
int blink_n = 0;
unsigned long previousMillis=0;
int info_n = 1;
 
bool infoLedState = LOW;
bool led_off = false;

int timedelay;
int velocity;
int stopped;
int degree;

void setup() {

  Serial.begin(115200);
  delay(10);

  pinMode(RED_LED_1, OUTPUT);
  pinMode(RED_LED_2, OUTPUT);
  pinMode(YELLOW_LED, OUTPUT);
  digitalWrite(YELLOW_LED, infoLedState);

  pinMode(BATTERY_READ, OUTPUT);
  ads.begin();

  if (ROBOT_ID == "00"){
    timedelay = 871;
    leftServo.attach(D4);
    rightServo.attach(D3);
  }
  else if (ROBOT_ID == "01"){
    timedelay = 790;
    leftServo.attach(D3);
    rightServo.attach(D4);
  }
  velocity = 1;
  stopped = 89;
  degree = 15;
  
  leftServo.write(stopped);
  rightServo.write(stopped);
  
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");

  server.begin();
  Serial.println("Web server running. Waiting for the ESP IP...");
  delay(10000);
  
  Serial.println(WiFi.localIP());
  
  delay(2000);
  
}

void loop() {

  // Read Digital Values
  servo_battery = ads.readADC_SingleEnded(2); 
  board_battery = ads.readADC_SingleEnded(3); 

  digitalWrite(RED_LED_1, red_led_1_state);
  digitalWrite(RED_LED_2, red_led_2_state);
  led_blink(info_n);

  WiFiClient client = server.available();
  
  if (client) {
    boolean blank_line = true;
    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        header += c;
        if (c == '\n' && blank_line) {
          client.println("HTTP/1.1 200 OK");
          client.println("Content-Type: text/html");
          client.println("Connection: close");
          client.println();
          if(header.indexOf("GET / HTTP/1.1") >= 0) {
            Serial.println(header);
          }
          else if(header.indexOf("GET /getid HTTP/1.1") >= 0){
            client.print(ROBOT_ID);
            client.print("-");
            client.print(WiFi.localIP());
          }
          else if(header.indexOf("GET /moveForward") >= 0){
            digitalWrite(BATTERY_READ, HIGH);
            float value = header.substring(16,21).toFloat();
            moveForward(value);
            String feedback = get_feedback();
            client.println(feedback);
            digitalWrite(BATTERY_READ, LOW);
          }
          else if(header.indexOf("GET /moveBack") >= 0){
            digitalWrite(BATTERY_READ, HIGH);
            float value = header.substring(13,18).toFloat();
            moveBack(value);
            String feedback = get_feedback();
            client.println(feedback);
            digitalWrite(BATTERY_READ, LOW);
          }
          else if(header.indexOf("GET /rotateLeft") >= 0){
            digitalWrite(BATTERY_READ, HIGH);
            float value = header.substring(15,20).toFloat();
            rotateLeft(value);
            String feedback = get_feedback();
            client.println(feedback);
            digitalWrite(BATTERY_READ, LOW);
          }
          else if(header.indexOf("GET /rotateRight") >= 0){
            digitalWrite(BATTERY_READ, HIGH);
            float value = header.substring(16,21).toFloat();
            rotateRight(value);
            String feedback = get_feedback();
            client.println(feedback);
            digitalWrite(BATTERY_READ, LOW);
          }
          else if(header.indexOf("GET /invert") >= 0){
            digitalWrite(BATTERY_READ, HIGH);
            Serial.print("invert");
            invert();
            String feedback = get_feedback();
            client.println(feedback);
            digitalWrite(BATTERY_READ, LOW);
          }
          else if(header.indexOf("GET /shiftUp") >= 0){
            digitalWrite(BATTERY_READ, HIGH);
            Serial.print("shiftUp");
            shiftUp();
            String feedback = get_feedback();
            client.println(feedback);
            digitalWrite(BATTERY_READ, LOW);
          }
          else if(header.indexOf("GET /shiftDown") >= 0){
            digitalWrite(BATTERY_READ, HIGH);
            Serial.print("shiftDown");
            shiftDown();
            String feedback = get_feedback();
            client.println(feedback);
            digitalWrite(BATTERY_READ, LOW);
          }
          else if(header.indexOf("GET /configStopValue") >= 0){
            digitalWrite(BATTERY_READ, HIGH);
            Serial.print(header.substring(20,25));
            int qtd = header.substring(20,25).toInt();
            configStopValue(qtd);
            String feedback = get_feedback();
            client.println(feedback);
            digitalWrite(BATTERY_READ, LOW);
          }
          else if(header.indexOf("GET /configDelay") >= 0){
            digitalWrite(BATTERY_READ, HIGH);
            Serial.print(header.substring(16,21));
            int qtd = header.substring(16,21).toInt();
            configDelay(qtd);
            String feedback = get_feedback();
            client.println(feedback);
            digitalWrite(BATTERY_READ, LOW);
          }
          else if(header.indexOf("GET /configGrauValue") >= 0){
            digitalWrite(BATTERY_READ, HIGH);
            Serial.print(header.substring(20,25));
            int qtd = header.substring(20,25).toInt();
            configGrauValue(qtd);
            String feedback = get_feedback();
            client.println(feedback);
            digitalWrite(BATTERY_READ, LOW);
          }
          header = "";
          break;
        }
        if (c == '\n') {
          blank_line = true;
        }
        else if (c != '\r') {
          blank_line = false;
        }
      }
    }
    delay(1);
    client.stop();
  }

  delay(200);
}

String get_feedback(){
  //Servo Battery
  servo_battery_divider_voltage = get_divider_voltage(servo_battery, servo_battery_max_digital_value, servo_battery_max_divider_voltage);
  servo_battery_source_voltage = get_source_voltage(servo_battery_divider_voltage, servo_battery_resistor1, servo_battery_resistor2);
  servo_battery_level = get_battery_level(servo_battery_source_voltage, servo_battery_power);
  String servo_battery = "Servo Battery: " + servo_battery_level + "\n";
  if(servo_battery_level == "Bad!!")
    digitalWrite(RED_LED_1, HIGH);
  else
    digitalWrite(RED_LED_1, LOW);
  
  //Board 
  board_battery_divider_voltage = get_divider_voltage(board_battery, board_battery_max_digital_value, board_battery_max_divider_voltage);
  board_battery_source_voltage = get_source_voltage(board_battery_divider_voltage, board_battery_resistor1, board_battery_resistor2);
  board_battery_level = get_battery_level(board_battery_source_voltage, board_battery_power);

  String feedback = servo_battery + "Board Battery: " + board_battery_level + "\n";

  if(board_battery_level == "Bad!!")
    digitalWrite(RED_LED_2, HIGH);
  else
    digitalWrite(RED_LED_2, LOW);
  
  return feedback;
}

void led_blink(int n){
  unsigned long currentMillis = millis(); 

  if ((unsigned long)(currentMillis - previousMillis) >= interval) {
    if(led_off == true){
      digitalWrite(YELLOW_LED, HIGH);
      blink_n--;
      if (blink_n <= 0){
          blink_n = 0;
          led_off = false;
      }
    }
 
    else {
      infoLedState = !infoLedState; 
      digitalWrite(YELLOW_LED, infoLedState); 
      blink_n++;
      if (blink_n > n * 2){
        led_off = true;
        blink_n = 2;
        infoLedState = LOW;
      }
    }
    previousMillis = millis();
  }
}



float get_divider_voltage(int digital_value, int max_digital_value, float max_divider_voltage)
{
  return ( ( (float)digital_value / max_digital_value) * max_divider_voltage );
}

float get_source_voltage(float divider_voltage, int Resistor_1, int Resistor_2)
{
  return ( divider_voltage / ( (float)Resistor_2 / (Resistor_1 + Resistor_2) ));
}

String get_battery_level(float source_voltage, float battery_power) {

  if(source_voltage < battery_power - drop_tolerance){
    return "Bad!!";
  }
  else{
    return "Good";
  }
  
}

void moveForward(float value){
  rightServo.write(stopped+(velocity*degree));
  leftServo.write(stopped-(velocity*degree));
  if(velocity == 2){
    delay((value*timedelay)*100/172);
  }else{
    delay(value*timedelay);
  }
  stopMovement();
}

void stopMovement(){
  leftServo.write(stopped);
  rightServo.write(stopped);
}

void moveBack(float value){
  rightServo.write(stopped-(velocity*degree));
  leftServo.write(stopped+(velocity*degree));
  if(velocity == 2){
    delay((value*timedelay)*100/172);
  }else{
    delay(value*timedelay);
  }
  stopMovement();
}

void rotateRight(float value){
  rightServo.write(stopped+(velocity*degree));
  leftServo.write(stopped+(velocity*degree));
  if(velocity == 2){
    delay(((value*timedelay*70*100)/(100*90*172)));
  }else{
    delay(((value*timedelay*70)/(100*90)));
  }
  stopMovement();
}

void rotateLeft (float value){
  rightServo.write(stopped-(velocity*degree));
  leftServo.write(stopped-(velocity*degree));
  if(velocity == 2){
    delay(((value*timedelay*70*100)/(100*90*172)));
  }else{
    delay(((value*timedelay*70)/(100*90)));
  }
  stopMovement();
}

void configGrauValue (int value){
  degree = value;
  timedelay = timedelay*(15/degree);
}

void configStopValue (int value){
  stopped = value;
  stopMovement();
}

void configDelay (int value){
  timedelay = value;
  timedelay = timedelay*(15/degree);
}

void invert(){
  Servo servob = leftServo;
  leftServo = rightServo;
  rightServo = servob;
}

void shiftUp(){
  if(velocity<2){
    velocity = velocity+1;
  }
}

void shiftDown(){
  if(velocity>1){
    velocity = velocity-1;
  }
}
