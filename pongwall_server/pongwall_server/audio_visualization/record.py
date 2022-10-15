import wave

import numpy as np
import pyaudio

SAMPLE_RATE = 44100
BUFFER_SIZE = 1024
RECORD_SECONDS = 10
CHANNELS = 2
FORMAT = pyaudio.paFloat32

OUTPUT_FILE = "output.wav"

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


def main() -> None:
    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=pyaudio.paFloat32,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=BUFFER_SIZE,
    )

    print("* recording *")
    frames = []

    for i in range(0, int(SAMPLE_RATE / BUFFER_SIZE * RECORD_SECONDS)):
        data = stream.read(BUFFER_SIZE)
        buffer = np.frombuffer(data, dtype=np.float32)
        buffer = np.reshape(buffer, (BUFFER_SIZE, 2))
        buffer = buffer[:, 0]
        output_data = buffer.tobytes()
        frames.append(output_data)

    print("* done recording *")

    stream.stop_stream()
    stream.close()
    pa.terminate()

    wf = wave.open(OUTPUT_FILE, "wb")
    wf.setnchannels(1)
    wf.setsampwidth(pa.get_sample_size(FORMAT))
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(b"".join(frames))
    wf.close()


if __name__ == "__main__":
    main()
