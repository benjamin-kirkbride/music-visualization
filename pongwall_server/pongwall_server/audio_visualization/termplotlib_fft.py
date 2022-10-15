#!/usr/bin/env python
# encoding: utf-8

## Module infomation ###
# Python (3.4.4)
# numpy (1.10.2)
# PyAudio (0.2.9)
# matplotlib (1.5.1)
# All 32bit edition
########################

import numpy as np
import pyaudio

import termplotlib as plt
import time


class SpectrumAnalyzer:
    FORMAT = pyaudio.paFloat32
    CHANNELS = 1
    # RATE = 16000
    RATE = 44100
    CHUNK = 128
    START = 0
    N = 128

    wave_x = 0
    wave_y = 0
    spec_x = 0
    spec_y = 0
    data = []

    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            output=False,
            frames_per_buffer=self.CHUNK,
        )
        self.next_plot_time = time.monotonic() + 0.2
        # Main loop
        self.loop()

    def loop(self):
        try:
            while True:
                self.data = self.audioinput()
                self.fft()
                if self.next_plot_time < time.monotonic():
                    print(chr(27) + "[2J")
                    self.next_plot_time = time.monotonic() + 0.2
                    self.graphplot()

        except KeyboardInterrupt:
            self.pa.close()

        print("End...")

    def audioinput(self):
        ret = self.stream.read(self.CHUNK)
        ret = np.frombuffer(ret, np.float32)
        return ret

    def fft(self):
        start = time.monotonic()
        self.spec_x = np.fft.fftfreq(self.N, d=1.0 / self.RATE)
        y = np.fft.fft(self.data[self.START : self.START + self.N])
        self.spec_y = [np.sqrt(c.real ** 2 + c.imag ** 2) for c in y]
        # print(self.spec_y)

    def graphplot(self):
        # Spectrum
        spectrum = plt.figure()
        spectrum.plot(self.spec_x, self.spec_y)
        # spectrum.axis([0, self.RATE / 2, 0, 50])
        spectrum.show()


if __name__ == "__main__":
    spec = SpectrumAnalyzer()
