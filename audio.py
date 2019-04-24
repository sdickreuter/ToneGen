import sounddevice as sd
from numpy import linspace

sd.default.samplerate = 192000
sd.default.device = 5

class Audio(object):
    def __init__(self,shepard):
        self.sample_rate = sd.default.samplerate#192000
        self.shepard = shepard
        self.stream = sd.OutputStream(channels=2, samplerate=self.sample_rate, blocksize=2048, dtype='float32', latency=0.01,
                                 callback=self.callback)
        print(sd.query_devices())

    def callback(self,outdata, frames, time, status):
        if status:
            print(status)
        print(time.outputBufferDacTime)
        t = linspace(time.outputBufferDacTime, time.outputBufferDacTime + frames/self.sample_rate, frames)
        #t = linspace(time.outputBufferDacTime, time.outputBufferDacTime + frames / self.sample_rate, frames)
        t,y =self.shepard.get_waveform(t)
        #y /= y.max()
        outdata[:, 0] = y
        outdata[:, 1] = y
        print(self.stream.time)

    def on(self):
        self.stream.start()

    def off(self):
        #print(self.stream.time)
        self.stream.stop()


