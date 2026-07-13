#include <TFT_eSPI.h>

TFT_eSPI tft = TFT_eSPI();

void setup() {
  Serial.begin(115200);
  delay(500);
  tft.init();
  tft.setRotation(0);
  tft.fillScreen(TFT_BLACK);

  tft.fillScreen(TFT_RED);
  delay(800);
  tft.fillScreen(TFT_GREEN);
  delay(800);
  tft.fillScreen(TFT_BLUE);
  delay(800);
  tft.fillScreen(TFT_WHITE);

  tft.setTextColor(TFT_BLACK, TFT_WHITE);
  tft.setTextSize(2);
  tft.setCursor(24, 42);
  tft.println("KEYCHAIN OS");
  tft.setCursor(24, 78);
  tft.println("DISPLAY OK");
}

void loop() {
}
