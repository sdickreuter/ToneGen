"""PyAudio Example: Play a wave file (callback version)."""

import pyaudio
import wave
import time
import sys
import numpy as np

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
                frames_per_buffer=2048,
                output=True,
                output_device_index=5,
                stream_callback=callback)

# start the stream (4)
stream.start_stream()

# wait for stream to finish (5)
while stream.is_active():
    time.sleep(0.1)

# stop stream (6)
stream.stop_stream()
stream.close()

# close PyAudio (7)
p.terminate()
