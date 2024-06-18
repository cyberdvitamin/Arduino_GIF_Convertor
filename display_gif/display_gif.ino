#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1  // Reset pin # (or -1 if sharing Arduino reset pin)
#define SCREEN_ADDRESS 0x3C  // I2C address of the display

// Initialize the OLED display
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Include the frame data
#include "frames.h"

void setup() {
  // Start I2C communication with custom pins: SDA = D6, SCL = D5
  Wire.begin(D6, D5);
  
  // Initialize the display
  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    //Serial.begin(115200);
    //Serial.println(F("SSD1306 allocation failed"));
    for (;;);  // Loop forever if allocation failed
  }
  display.clearDisplay();
  display.display();
  //Serial.begin(115200);
  //Serial.println(F("SSD1306 initialized successfully"));
}

void loop() {
  for (int i = START; i < NUM_FRAMES; i++) {
    display.clearDisplay();
    display.drawBitmap(0, 0, frames[i], SCREEN_WIDTH, SCREEN_HEIGHT, SSD1306_WHITE);
    display.display();
    delay(FRAME_DELAY);
    //Serial.print(F("Displaying frame "));
    //Serial.println(i);
  }
}
