import sounddevice as sd
import numpy as np
import billiard as mp
mp.forking_enable(False)
import queue
import shepard as shepard
import tones
import dill

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

blocksize = 2048



class Audio(object):
    def __init__(self,param_queue,sample_rate=None,device_index=None):
        if device_index is None:
            device_index = default_device
        if sample_rate is None:
            sample_rate = default_samplerate


        self.sample_rate = sample_rate
        self.device_index = device_index
        self.param_queue = param_queue
        self.buffer_queue = mp.Queue()

        self.shepard = shepard.ShepardTone(tones.freqs[0]*2**5, 1, 100, 0, 0.5,20.0,100000.0)
        self.currentframe = 0

        self.stream = sd.OutputStream(channels=2,device=self.device_index, samplerate=self.sample_rate, blocksize=blocksize, dtype='float32', latency=0.1,
                                 callback=self._callback)
        #print(sd.query_devices())
        self.buffer_process = mp.Process(target=self._generate_buffer)
        self.buffer_process.start()

    def _generate_buffer(self):
        while True:
            while self.buffer_queue.qsize() < 5:
                t = np.linspace(self.currentframe, self.currentframe + blocksize, blocksize, dtype=np.float32)
                t /= self.sample_rate

                self.buffer_queue.put(dill.dumps(self.shepard.get_waveform(t)))
                self.currentframe += blocksize
            try:
                starting_freq, n, envelope_width, envelope_x0, volume, low_cutoff, high_cutoff = self.param_queue.get_nowait()
                self.shepard.set(starting_freq, n, envelope_width, envelope_x0, volume, low_cutoff, high_cutoff)
            except queue.Empty:
                pass

    # try:
        #     name, value = self.input_queue.get_nowait()
        #     #starting_freq, n, envelope_width, envelope_x0, volume, low_cutoff, high_cutoff
        #
        #     if name == 'starting_freq':
        #         self.shepard.starting_freq = value
        #     elif name == 'n':
        #         self.shepard.n = value
        #     elif name == 'envelope_width':
        #         self.shepard.envelope_width = value
        #     elif name == 'envelope_x0':
        #         self.shepard.envelope_x0 = value
        #     elif name == 'volume':
        #         self.shepard.volume = value
        #     elif name == 'low_cutoff':
        #         self.shepard.low_cutoff = value
        #     elif name == 'high_cutoff':
        #         self.shepard.high_cutoff = value
        # except queue.Empty:
        #     pass


    def _callback(self,outdata, frames, time, status):
        if status:
            print(status)

        y = dill.loads(self.buffer_queue.get())
        outdata[:, 0] = y
        outdata[:, 1] = y

    def on(self):
        self.stream.start()

    def off(self):
        self.stream.stop()
        for i in range(10):
            try:
                self.buffer_queue.get_nowait()
            except queue.Empty:
                break
        self.currentframe = 0

        #self.buffer_process = None
        #print(self.stream.time)


    def __del__(self):
        self.stream = None
        self.buffer_process.terminate()
        sd.stop()

