#define LCD_BL 6

void setup() {
  Serial.begin(115200);
  delay(500);
  pinMode(LCD_BL, OUTPUT);
  digitalWrite(LCD_BL, HIGH);
  Serial.println("Backlight GPIO6 set HIGH");
}

void loop() {
}
