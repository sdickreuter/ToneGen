import pyaudio
import wave
import time
import sys
import numpy as np


pa = pyaudio.PyAudio()

default_device = pa.get_default_output_device_info()['index']
print(default_device)
devices = []
for i in range(pa.get_device_count()):
    devices.append(pa.get_device_info_by_index(i))

device_names = []
device_indices = []
devices_defaultsamplerate = []
for d in devices:
    if d['maxOutputChannels'] > 1:
        device_names.append(d['name'])
        device_indices.append(d['index'])
        devices_defaultsamplerate.append(d['defaultSampleRate'])

print(device_names)


class Audio(object):
    def __init__(self,shepard,device_index=None,sample_rate=None):
        self.pa = pyaudio.PyAudio()
        default_device = self.pa.get_default_output_device_info()
        if device_index is None:
            device_index = int(default_device['index'])
        if sample_rate is None:
            sample_rate = int(default_device['defaultSampleRate'])

        self.sample_rate = sample_rate
        self.device_index = device_index
        self.shepard = shepard

        self.stream = self.pa.open(format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                frames_per_buffer=2048,
                output=True,
                output_device_index=self.device_index,
                stream_callback=self.callback)
        self.stream.stop_stream()

    def callback(self, in_data, frame_count, time_info, status):
        if status:
            print(status)
        #time = self.stream.get_time()
        #print(time.outputBufferDacTime)
        #print(time_info)
        now = time_info['output_buffer_dac_time']
        t = np.linspace(now, now + frame_count/self.sample_rate, frame_count,dtype=np.float32)
        #t = linspace(time.outputBufferDacTime, time.outputBufferDacTime + frames / self.sample_rate, frames)
        y =self.shepard.get_waveform(t)
        #print(y)
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
