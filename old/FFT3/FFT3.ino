/*
 * A simple hardware test which receives audio from the audio shield
 * Line-In pins and send it to the Line-Out pins and headphone jack.
 *
 * This example code is in the public domain.
 */

#include <Audio.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <SerialFlash.h>

const int bins = 24;

// // GUItool: begin automatically generated code
// AudioInputI2S audio_input;   //xy=200,69
// AudioOutputI2S audio_output; //xy=365,94
// AudioConnection patch_cord1(audio_input, 0, audio_output, 0);
// AudioConnection patch_cord2(audio_input, 1, audio_output, 1);
// AudioControlSGTL5000 audio_shield; //xy=302,184
// // GUItool: end automatically generated code

// GUItool: begin automatically generated code
AudioInputI2S audio_input;   //xy=753,364
AudioMixer4 mixer1;          //xy=926,407
AudioOutputI2S audio_output; //xy=1006,305
AudioAnalyzeFFT1024 fft1024; //xy=1081,420
AudioConnection patch_cord1(audio_input, 0, mixer1, 0);
AudioConnection patch_cord2(audio_input, 0, audio_output, 0);
AudioConnection patch_cord3(audio_input, 1, mixer1, 1);
AudioConnection patch_cord4(audio_input, 1, audio_output, 1);
AudioConnection patch_cord5(mixer1, fft1024);
AudioControlSGTL5000 audio_shield; //xy=916.8887786865234,524.0000667572021
// GUItool: end automatically generated code

const int myInput = AUDIO_INPUT_LINEIN;
//const int myInput = AUDIO_INPUT_MIC;

// The scale sets how much sound is needed in each frequency range to
// show all 8 bars.  Higher numbers are more sensitive.
float scale = 60.0;

// An array to hold the 16 frequency bands
float level[bins];

void setup()
{
  // Audio connections require memory to work.  For more
  // detailed information, see the MemoryAndCpuUsage example
  AudioMemory(12);

  // Enable the audio shield, select input, and enable output
  audio_shield.enable();
  audio_shield.inputSelect(myInput);
  audio_shield.volume(0.5);

  // configure the mixer to equally add left & right
  mixer1.gain(0, 0.5);
  mixer1.gain(1, 0.5);

  fft1024.windowFunction(AudioWindowFlattop1024);
}

elapsedMillis volmsec = 0;

void loop()
{
  if (fft1024.available())
  {
    // read the 512 FFT frequencies into 16 levels
    // music is heard in octaves, but the FFT data
    // is linear, so for the higher octaves, read
    // many FFT bins together.
    level[0] = fft1024.read(0, 2);
    level[1] = fft1024.read(3, 3);
    level[2] = fft1024.read(4, 5);
    level[3] = fft1024.read(6, 7);
    level[4] = fft1024.read(8, 9);
    level[5] = fft1024.read(10, 12);
    level[6] = fft1024.read(13, 15);
    level[7] = fft1024.read(16, 19);
    level[8] = fft1024.read(20, 23);
    level[9] = fft1024.read(24, 29);
    level[10] = fft1024.read(30, 35);
    level[11] = fft1024.read(36, 43);
    level[12] = fft1024.read(44, 52);
    level[13] = fft1024.read(53, 63);
    level[14] = fft1024.read(64, 75);
    level[15] = fft1024.read(76, 90);
    level[16] = fft1024.read(91, 108);
    level[17] = fft1024.read(109, 129);
    level[18] = fft1024.read(130, 155);
    level[19] = fft1024.read(156, 184);
    level[20] = fft1024.read(185, 220);
    level[21] = fft1024.read(221, 262);
    level[22] = fft1024.read(263, 312);
    level[23] = fft1024.read(313, 372);

    // See this conversation to change this to more or less than 16 log-scaled bands?
    // https://forum.pjrc.com/threads/32677-Is-there-a-logarithmic-function-for-FFT-bin-selection-for-any-given-of-bands
    Serial.print("\033[2J");
    Serial.print("\033[H");
    for (int i = 0; i < bins; i++)
    {
      Serial.print(i);
      Serial.print(": ");
      int level_bar_length = level[i] * 1000;
      for (int i = 0; i < level_bar_length; i++)
      {
        Serial.print("#");
      }
      Serial.println();
    }
  }
}
