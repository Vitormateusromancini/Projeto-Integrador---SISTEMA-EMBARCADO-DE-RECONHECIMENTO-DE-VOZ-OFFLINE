#include <Arduino.h>

const int MIC_PIN = 34;

const uint32_t SAMPLE_RATE = 8000; // 8 kHz
const uint16_t SAMPLES_PER_PACKET = 160;
const uint16_t BYTES_PER_PACKET   = SAMPLES_PER_PACKET * 2;

void setup() {
  Serial.begin(230400);
  pinMode(MIC_PIN, INPUT);
}

void loop() {
  static uint8_t buffer[BYTES_PER_PACKET];
  const uint32_t us_per_sample = 1000000UL / SAMPLE_RATE;

  for (uint16_t i = 0; i < SAMPLES_PER_PACKET; i++) {
    uint32_t t0 = micros();

    int raw = analogRead(MIC_PIN);  // 0..4095

    // Centraliza e aplica GANHO
    int16_t sample = (int16_t)((raw - 2048) * 16);

    buffer[2 * i]     = (uint8_t)(sample & 0xFF);
    buffer[2 * i + 1] = (uint8_t)((sample >> 8) & 0xFF);

    while (micros() - t0 < us_per_sample) {
      // nada
    }
  }

  Serial.write(buffer, BYTES_PER_PACKET);
}
