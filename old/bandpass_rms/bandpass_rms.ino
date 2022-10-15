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

// GUItool: begin automatically generated code
AudioInputI2S audio_input;   //xy=753.8888168334961,364.00001525878906
AudioMixer4 mixer1;          //xy=938.8889312744141,428.88887786865234
AudioOutputI2S audio_output; //xy=1006.8888168334961,305.00001525878906
AudioFilterBiquad biquad1;   //xy=1112.8890647888184,428.88891792297363
AudioAnalyzeRMS rms1;        //xy=1294.8890342712402,428.88890504837036
AudioConnection patchCord1(audio_input, 0, audio_output, 0);
AudioConnection patchCord2(audio_input, 0, mixer1, 0);
AudioConnection patchCord3(audio_input, 1, audio_output, 1);
AudioConnection patchCord4(audio_input, 1, mixer1, 1);
AudioConnection patchCord5(mixer1, biquad1);
AudioConnection patchCord6(biquad1, rms1);
AudioControlSGTL5000 audio_shield; //xy=916.8887939453125,523.000093460083
// GUItool: end automatically generated code

const int myInput = AUDIO_INPUT_LINEIN;
//const int myInput = AUDIO_INPUT_MIC;

// The scale sets how much sound is needed in each frequency range to
// show all 8 bars.  Higher numbers are more sensitive.
float scale = 60.0;

// An array to hold the 16 frequency bands
float level[16];

// This array holds the on-screen levels.  When the signal drops quickly,
// these are used to lower the on-screen level 1 bar per update, which
// looks more pleasing to corresponds to human sound perception.
int shown[16];

void setup()
{
  // Audio connections require memory to work.  For more
  // detailed information, see the MemoryAndCpuUsage example
  AudioMemory(12);

  // Enable the audio shield, select input, and enable output
  audio_shield.enable();
  audio_shield.inputSelect(myInput);
  audio_shield.volume(0.5);

  biquad1.setLowShelf(0, 890, -100, 0.5);
  biquad1.setHighShelf(1, 1109, -100, 0.5);

  // configure the mixer to equally add left & right
  mixer1.gain(0, 0.5);
  mixer1.gain(1, 0.5);
}

elapsedMillis volmsec = 0;

void loop()
{
  if (rms1.available())
  {
    Serial.print("\033[2J");
    Serial.print("\033[H");
    int rms_bar_length = rms1.read() * 1000;
    for (int i = 0; i < rms_bar_length; i++)
    {
      Serial.print("#");
    }
    Serial.println();
  }
}
