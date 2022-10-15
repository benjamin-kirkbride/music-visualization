import pyaudio
import numpy as np
import signal
import time


SAMPLE_RATE = 44100
TIME_STEP = 1 / SAMPLE_RATE

BUFFER_SIZE = 256

NEXT_FFT_TIME = time.monotonic() + 1


def fftPlot(buffer, time_step):
    # here it's assumes analytic signal (real signal...)- so only half of the axis is required

    t = np.arange(0, buffer.shape[-1]) * time_step

    if buffer.shape[0] % 2 != 0:
        print("signal prefered to be even in size, autoFixing it...")
        t = t[0:-1]
        sig = sig[0:-1]

    sigFFT = np.fft.fft(buffer) / t.shape[0]  # divided by size t for coherent magnitude

    freq = np.fft.fftfreq(t.shape[0], d=time_step)

    # plot analytic signal - right half of freq axis needed only...
    firstNegInd = np.argmax(freq < 0)
    freqAxisPos = freq[0:firstNegInd]
    sigFFTPos = 2 * sigFFT[0:firstNegInd]  # *2 because of magnitude of analytic signal

    return sigFFTPos, freqAxisPos


def _callback(in_data, frame_count, time_info, status):
    global NEXT_FFT_TIME
    if NEXT_FFT_TIME < time.monotonic():
        NEXT_FFT_TIME = NEXT_FFT_TIME + (1 / 30)

        audio_buffer = np.frombuffer(in_data, dtype=np.float32)

        print(chr(27) + "[2J")
        print(fftPlot(audio_buffer, TIME_STEP))

    return None, pyaudio.paContinue


def main():
    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=pyaudio.paFloat32,
        channels=1,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=BUFFER_SIZE,
        stream_callback=_callback,
    )

    signal.pause()


if __name__ == "__main__":
    main()
