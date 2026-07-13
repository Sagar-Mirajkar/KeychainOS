#include <SPI.h>
#include <SD.h>

#define SPI_MISO 42
#define SPI_MOSI 2
#define SPI_SCLK 1
#define LCD_CS 39
#define SD_CS 38

SPIClass displaySPI(FSPI);

void setup() {
  Serial.begin(115200);
  delay(500);

  pinMode(LCD_CS, OUTPUT);
  pinMode(SD_CS, OUTPUT);
  digitalWrite(LCD_CS, HIGH);
  digitalWrite(SD_CS, HIGH);

  displaySPI.begin(SPI_SCLK, SPI_MISO, SPI_MOSI, -1);

  if (!SD.begin(SD_CS, displaySPI)) {
    Serial.println("FAIL: SD mount failed");
    return;
  }

  if (SD.cardType() == CARD_NONE) {
    Serial.println("FAIL: No SD card detected");
    return;
  }

  uint64_t cardSizeMB = SD.cardSize() / (1024ULL * 1024ULL);
  Serial.printf("SD size: %llu MB\n", cardSizeMB);

  File testFile = SD.open("/keychain_test.txt", FILE_WRITE);
  if (!testFile) {
    Serial.println("FAIL: Could not create test file");
    return;
  }

  testFile.println("KeychainOS SD test passed.");
  testFile.close();
  Serial.println("PASS: SD mounted and file written");
}

void loop() {
}
