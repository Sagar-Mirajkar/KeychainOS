#include <TFT_eSPI.h>

TFT_eSPI tft = TFT_eSPI();

void setup() {
  Serial.begin(115200);
  delay(500);

  tft.init();
  tft.setRotation(0);
  tft.fillScreen(TFT_BLACK);

  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  tft.setTextSize(2);
  tft.setCursor(28, 40);
  tft.println("KEYCHAIN OS");

  tft.setTextSize(1);
  tft.setCursor(28, 80);
  tft.println("Firmware shell placeholder");
}

void loop() {
}
