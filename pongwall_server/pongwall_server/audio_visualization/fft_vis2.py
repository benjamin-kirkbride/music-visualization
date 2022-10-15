import signal
import sys
import time

import aubio
import numpy as np
import pyaudio

SAMPLE_RATE = 44100
BUFFER_SIZE = 512

FILTERBANK_BINS = [
    0,
    22,
    46,
    72,
    101,
    133,
    167,
    205,
    247,
    292,
    342,
    397,
    457,
    523,
    595,
    674,
    760,
    855,
    958,
    1072,
    1197,
    1333,
    1483,
    1647,
    1827,
    2023,
    2239,
    2475,
    2734,
    3018,
    3329,
    3670,
    4044,
    4453,
    4901,
    5393,
    5931,
    6521,
    7167,
    7876,
    8652,
    9503,
    10435,
    11456,
    12575,
    13802,
    15146,
    16618,
    18232,
    20000,
]

NEXT_FFT_TIME = time.monotonic() + 1


def _callback(in_data, frame_count, time_info, status):
    global NEXT_FFT_TIME
    if NEXT_FFT_TIME < time.monotonic():
        # refresh every half second
        NEXT_FFT_TIME = NEXT_FFT_TIME + (1 / 2)

        # get just the left channel
        audio_buffer = np.frombuffer(in_data, dtype=np.float32)

        # if sys.argv[1] == "stereo":
        #     # comment out next two lines and set channels=1 in main() to switch to mono
        #     audio_buffer = np.reshape(audio_buffer, (BUFFER_SIZE, 2))
        #     audio_buffer = audio_buffer[:, 0]

        if sys.argv[1] == "stereo":
            # comment out next two lines and set channels=1 in main() to switch to mono
            audio_buffer = np.reshape(audio_buffer, (BUFFER_SIZE, 2))
            audio_buffer = audio_buffer[:, 0]
            audio_buffer = np.copy(audio_buffer)

        fft = aubio.fft(BUFFER_SIZE)(audio_buffer)
        fb = aubio.filterbank(48, BUFFER_SIZE)
        fb.set_power(2)
        fb.set_triangle_bands(aubio.fvec(FILTERBANK_BINS), SAMPLE_RATE)

        output = np.around(fb(fft))

        print(chr(27) + "[2J")
        print("\033[H")
        print(f"Audio: {audio_buffer.any()}")
        for bin_, amplitude in np.column_stack((FILTERBANK_BINS[1:-1], output)):
            print(f"{bin_}: {np.around(amplitude)}")

    return (None, pyaudio.paContinue)


def main() -> None:
    try:
        if sys.argv[1] != "mono" and sys.argv[1] != "stereo":
            sys.exit("arg must be either 'mono' or 'stereo'")
    except IndexError:
        sys.exit("arg must be either 'mono' or 'stereo'")

    if sys.argv[1] == "mono":
        channels = 1
    else:
        channels = 2

    pyaudio.PyAudio().open(
        format=pyaudio.paFloat32,
        channels=channels,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=BUFFER_SIZE,
        stream_callback=_callback,
    )

    signal.pause()


if __name__ == "__main__":
    main()
