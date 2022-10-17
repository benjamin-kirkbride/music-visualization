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

const int bins_qty = 24;

// GUItool: begin automatically generated code
AudioInputUSB audio_input;   //xy=612.8888244628906,234.99999809265137
AudioAnalyzeFFT1024 l_fft;   //xy=860.8888282775879,335.00001335144043
AudioAnalyzeFFT1024 r_fft;   //xy=862.8889274597168,374.8888969421387
AudioOutputI2S audio_output; //xy=871.8888549804688,233
AudioConnection patchCord1(audio_input, 0, audio_output, 0);
AudioConnection patchCord2(audio_input, 0, l_fft, 0);
AudioConnection patchCord3(audio_input, 1, audio_output, 1);
AudioConnection patchCord4(audio_input, 1, r_fft, 0);
AudioControlSGTL5000 audio_shield; //xy=624.8888511657715,357.0000057220459
// GUItool: end automatically generated code

const int myInput = AUDIO_INPUT_LINEIN;

// An array to hold the bins
float l_bins[bins_qty];
float r_bins[bins_qty];

void setup()
{
  // Audio connections require memory to work.  For more
  // detailed information, see the MemoryAndCpuUsage example
  // https://forum.pjrc.com/threads/55224-Using-two-instances-of-AudioAnalyzeFFT1024-at-the-same-time?p=198887&viewfull=1#post198887
  AudioMemory(48);

  // Enable the audio shield, select input, and enable output
  audio_shield.enable();
  audio_shield.inputSelect(myInput);
  audio_shield.volume(0.5);

  l_fft.windowFunction(AudioWindowFlattop1024);
  r_fft.windowFunction(AudioWindowFlattop1024);
}

//
unsigned long prints = 0;
bool l_fft_recieved = false;
bool r_fft_recieved = false;

void loop()
{
  if (l_fft.available())
  {
    l_bins[0] = l_fft.read(0, 2);
    l_bins[1] = l_fft.read(3, 3);
    l_bins[2] = l_fft.read(4, 5);
    l_bins[3] = l_fft.read(6, 7);
    l_bins[4] = l_fft.read(8, 9);
    l_bins[5] = l_fft.read(10, 12);
    l_bins[6] = l_fft.read(13, 15);
    l_bins[7] = l_fft.read(16, 19);
    l_bins[8] = l_fft.read(20, 23);
    l_bins[9] = l_fft.read(24, 29);
    l_bins[10] = l_fft.read(30, 35);
    l_bins[11] = l_fft.read(36, 43);
    l_bins[12] = l_fft.read(44, 52);
    l_bins[13] = l_fft.read(53, 63);
    l_bins[14] = l_fft.read(64, 75);
    l_bins[15] = l_fft.read(76, 90);
    l_bins[16] = l_fft.read(91, 108);
    l_bins[17] = l_fft.read(109, 129);
    l_bins[18] = l_fft.read(130, 155);
    l_bins[19] = l_fft.read(156, 184);
    l_bins[20] = l_fft.read(185, 220);
    l_bins[21] = l_fft.read(221, 262);
    l_bins[22] = l_fft.read(263, 312);
    l_bins[23] = l_fft.read(313, 372);

    if (l_fft_recieved)
    {
      // the right channel was not available prior to this running twice (not good)
      prints = prints + 1;
    }

    Serial.print("l:");
    Serial.print(prints);
    Serial.print(":");
    // print the first l_bins outside the loop to prevent preceding comma
    Serial.print(l_bins[0], 16);
    for (int i = 1; i < bins_qty; i++)
    {
      Serial.print(",");
      Serial.print(l_bins[i], 16);
    }
    Serial.println();
    l_fft_recieved = true;
  }

  if (r_fft.available())
  {
    r_bins[0] = r_fft.read(0, 2);
    r_bins[1] = r_fft.read(3, 3);
    r_bins[2] = r_fft.read(4, 5);
    r_bins[3] = r_fft.read(6, 7);
    r_bins[4] = r_fft.read(8, 9);
    r_bins[5] = r_fft.read(10, 12);
    r_bins[6] = r_fft.read(13, 15);
    r_bins[7] = r_fft.read(16, 19);
    r_bins[8] = r_fft.read(20, 23);
    r_bins[9] = r_fft.read(24, 29);
    r_bins[10] = r_fft.read(30, 35);
    r_bins[11] = r_fft.read(36, 43);
    r_bins[12] = r_fft.read(44, 52);
    r_bins[13] = r_fft.read(53, 63);
    r_bins[14] = r_fft.read(64, 75);
    r_bins[15] = r_fft.read(76, 90);
    r_bins[16] = r_fft.read(91, 108);
    r_bins[17] = r_fft.read(109, 129);
    r_bins[18] = r_fft.read(130, 155);
    r_bins[19] = r_fft.read(156, 184);
    r_bins[20] = r_fft.read(185, 220);
    r_bins[21] = r_fft.read(221, 262);
    r_bins[22] = r_fft.read(263, 312);
    r_bins[23] = r_fft.read(313, 372);

    if (r_fft_recieved)
    {
      // the right channel was not available prior to this running twice (not good)
      prints = prints + 1;
    }

    Serial.print("r:");
    Serial.print(prints);
    Serial.print(":");
    // print the first r_bins outside the loop to prevent preceding comma
    Serial.print(r_bins[0], 16);
    for (int i = 1; i < bins_qty; i++)
    {
      Serial.print(",");
      Serial.print(r_bins[i], 16);
    }
    Serial.println();
    r_fft_recieved = true;
  }
  if (l_fft_recieved && r_fft_recieved)
  {
    l_fft_recieved = false;
    r_fft_recieved = false;
    prints = prints + 1;
  }
}
