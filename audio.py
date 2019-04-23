"""PyAudio Example: Play a wave file (callback version)."""

import pyaudio
import wave
import time
import sys
import numpy as np

# instantiate PyAudio (1)
p = pyaudio.PyAudio()

# define callback (2)
def callback(in_data, frame_count, time_info, status):
    data = np.sin(np.arange(50000)/20)
    data = data.astype(np.float32).tostring()
    return (data, pyaudio.paContinue)

# open stream using callback (3)
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=44100,
                frames_per_buffer=1024,
                output=True,
                output_device_index=2,
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
