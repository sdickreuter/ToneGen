import pyaudio
import wave
import time
import sys
import numpy as np


class Audio(object):
    def __init__(self,shepard):
        self.sample_rate = 192000
        self.shepard = shepard
        self.pa = pyaudio.PyAudio()
        print(self.pa.get_default_output_device_info())
        for i in range(self.pa.get_device_count()):
            print(self.pa.get_device_info_by_index(i))

        self.stream = self.pa.open(format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                frames_per_buffer=1024,
                output=True,
                output_device_index=5,
                stream_callback=self.callback)
        self.stream.stop_stream()

    def callback(self, in_data, frame_count, time_info, status):
        if status:
            print(status)
        #time = self.stream.get_time()
        #print(time.outputBufferDacTime)
        #print(time_info)
        now = time_info['output_buffer_dac_time']
        t = np.linspace(now, now + frame_count/self.sample_rate, frame_count)
        #t = linspace(time.outputBufferDacTime, time.outputBufferDacTime + frames / self.sample_rate, frames)
        t,y =self.shepard.get_waveform(t)
        y /= y.max()
        #print(self.stream.get_time())
        data = y.astype(np.float32).tostring()
        return (data, pyaudio.paContinue)

    def on(self):
        self.stream.start_stream()

    def off(self):
        #print(self.stream.time)
        self.stream.stop_stream()

    def __del__(self):
        if self.stream.is_active():
            self.stream.stop_stream()
            self.stream.close()

        # close PyAudio (7)
        self.pa.terminate()
