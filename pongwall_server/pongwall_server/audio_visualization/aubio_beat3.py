import pyaudio
import numpy as np
import aubio
import signal
import sys
import time

import argparse

from typing import List, NamedTuple, Tuple

import termplotlib as plt


class ClientInfo(NamedTuple):
    ip: str
    port: int
    address: str


parser = argparse.ArgumentParser()
parser.add_argument(
    "-c",
    "--client",
    help="OSC Client address (multiple can be provided)",
    nargs=3,
    action="append",
    metavar=("IP", "PORT", "ADDRESS"),
    required=False,
)
parser.add_argument(
    "-b",
    "--bufsize",
    help="Size of audio buffer for beat detection (default: 128)",
    default=128,
    type=int,
)
parser.add_argument("-v", "--verbose", help="Print BPM on beat", action="store_true")
args = parser.parse_args()


class BeatPrinter:
    def print_bpm(self, bpm: float) -> None:
        print(f"{bpm:.1f}")
        sys.stdout.flush()


class BeatDetector:
    def __init__(self, buf_size: int):
        self.buf_size: int = buf_size

        # Set up pyaudio and aubio beat detector
        self.p: pyaudio.PyAudio = pyaudio.PyAudio()

        self.samplerate: int = 44100
        self.stream: pyaudio.Stream = self.p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=self.samplerate,
            input=True,
            frames_per_buffer=self.buf_size,
            stream_callback=self._pyaudio_callback,
        )

        self.next_plot_time = time.monotonic() + (1 / 60)

        self.spec_x = []
        self.spec_y = []
        self.spectrum = plt.figure()

        fft_size: int = self.buf_size * 2
        # self.tempo: aubio.tempo = aubio.tempo(
        #     "default", fft_size, self.buf_size, self.samplerate
        # )

        self.spinner: BeatPrinter = BeatPrinter()

    def _pyaudio_callback(self, in_data, frame_count, time_info, status):
        if self.next_plot_time < time.monotonic():
            audio_buffer = np.frombuffer(in_data, dtype=np.float32)

            self.spec_x = np.fft.fftfreq(self.buf_size, d=1.0 / self.samplerate)
            y = np.fft.fft(audio_buffer[0 : 0 + self.buf_size])
            self.spec_y = [np.sqrt(c.real ** 2 + c.imag ** 2) for c in y]
            print(chr(27) + "[2J")
            print(np.around(self.spec_y, 2))
            self.next_plot_time = time.monotonic() + (1 / 60)

        return None, pyaudio.paContinue  # Tell pyAudio to continue

    def __del__(self):
        self.stream.close()
        self.p.terminate()


def main():
    bd = BeatDetector(args.bufsize)

    signal.pause()  # Audio processing happens in separate thread, so put this thread to sleep


if __name__ == "__main__":
    main()
