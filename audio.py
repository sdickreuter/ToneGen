import sounddevice as sd
import numpy as np

default_device = sd.query_hostapis(0)['default_output_device']

devices = sd.query_devices()

device_names = []
device_indices = []
devices_defaultsamplerate = []
for i in range(len(devices)):
    d = devices[i]
    if d['max_output_channels'] > 1:
        device_names.append(d['name'])
        device_indices.append(i)
        devices_defaultsamplerate.append(d['default_samplerate'])

default_samplerate = devices_defaultsamplerate[device_indices.index(default_device)]




class Audio(object):
    def __init__(self,shepard,sample_rate=None,device_index=None):
        if device_index is None:
            device_index = default_device
        if sample_rate is None:
            sample_rate = default_samplerate


        self.sample_rate = sample_rate
        self.device_index = device_index
        self.shepard = shepard
        self.stream = sd.OutputStream(channels=2,device=self.device_index, samplerate=self.sample_rate, blocksize=2048, dtype='float32', latency=0.01,
                                 callback=self.callback)
        #print(sd.query_devices())

    def callback(self,outdata, frames, time, status):
        if status:
            print(status)
        #print(time.outputBufferDacTime)
        t = np.linspace(time.outputBufferDacTime, time.outputBufferDacTime + frames/self.sample_rate, frames,dtype=np.float32)
        #t = linspace(time.outputBufferDacTime, time.outputBufferDacTime + frames / self.sample_rate, frames)
        y = self.shepard.get_waveform(t)
        #print(y)
        #y /= y.max()
        outdata[:, 0] = y
        outdata[:, 1] = y
        #print(self.stream.time)

    def on(self):
        self.stream.start()

    def off(self):
        #print(self.stream.time)
        self.stream.stop()

    def __del__(self):
        self.stream = None
        sd.stop()

