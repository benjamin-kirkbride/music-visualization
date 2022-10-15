import pyaudio
import numpy as np
import aubio
import signal
import sys

import argparse

from typing import List, NamedTuple, Tuple


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

        samplerate: int = 44100
        self.stream: pyaudio.Stream = self.p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=samplerate,
            input=True,
            frames_per_buffer=self.buf_size,
            stream_callback=self._pyaudio_callback,
        )

        fft_size: int = self.buf_size * 2
        self.tempo: aubio.tempo = aubio.tempo(
            "default", fft_size, self.buf_size, samplerate
        )

        self.spinner: BeatPrinter = BeatPrinter()

    def _pyaudio_callback(self, in_data, frame_count, time_info, status):
        audio_buffer = np.frombuffer(in_data, dtype=np.float32)

        fourier = np.fft.fft(audio_buffer[0 : 0 + self.buf_size])
        fourier = [np.sqrt(c.real ** 2 + c.imag ** 2) for c in fourier]

        print(np.around(fourier, decimals=1))

        beat = self.tempo(audio_buffer)
        if beat[0]:
            if args.verbose:
                self.spinner.print_bpm(self.tempo.get_bpm())

        return None, pyaudio.paContinue  # Tell pyAudio to continue

    def __del__(self):
        self.stream.close()
        self.p.terminate()


def main():
    bd = BeatDetector(args.bufsize)

    signal.pause()  # Audio processing happens in separate thread, so put this thread to sleep


if __name__ == "__main__":
    main()
