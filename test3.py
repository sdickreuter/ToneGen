"""PyAudio Example: Play a wave file (callback version)."""

import pyaudio
import wave
import time
import sys
import numpy as np


class Audio(object):
    def __init__(self,shepard):
        self.sample_rate = 44100#192000
        self.shepard = shepard
        self.pa = pyaudio.PyAudio()

        self.stream = stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=sample_rate,
                frames_per_buffer=0,
                output=True,
                output_device_index=8,
                stream_callback=self.callback)
        print(self.pa.get_default_output_device_info())

    def callback(self,outdata, frames, time, status):
        if status:
            print(status)
        time = self.stream.get_time()
        #print(time.outputBufferDacTime)
        t = np.linspace(time, time + frames/self.sample_rate, frames)
        #t = linspace(time.outputBufferDacTime, time.outputBufferDacTime + frames / self.sample_rate, frames)
        t,y =self.shepard.get_waveform(t)
        y /= y.max()
        outdata[:, 0] = y
        outdata[:, 1] = y
        print(self.stream.time)

    def on(self):
        self.stream.start_stream()

    def off(self):
        #print(self.stream.time)
        self.stream.stop_stream()

    def __del__(self):
        self.stream.stop_stream()
        self.stream.close()

        # close PyAudio (7)
        self.pa.terminate()


A_freq = 440

sample_rate = 192000
T = 0.25
t = np.linspace(0, T, T * sample_rate, False)

# instantiate PyAudio (1)
p = pyaudio.PyAudio()

# define callback (2)
def callback(in_data, frame_count, time_info, status):
    #print(time_info)
    current_time = list(time_info.values())[1]
    t = np.linspace(current_time, current_time + frame_count/sample_rate, frame_count)
    audio = np.sin(A_freq * t * 2 * np.pi)
    data = audio.astype(np.float32).tostring()
    return (data, pyaudio.paContinue)

# open stream using callback (3)
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=sample_rate,
                frames_per_buffer=0,
                output=True,
                output_device_index=5,
                stream_callback=callback)

# start the stream (4)
stream.start_stream()

# wait for stream to finish (5)
while stream.is_active():
    print(stream.get_time())
    time.sleep(0.1)

# stop stream (6)
stream.stop_stream()
