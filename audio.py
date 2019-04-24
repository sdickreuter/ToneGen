import sounddevice as sd
import numpy as np


class Audio(object):
    def __init__(self,shepard):
        self.sample_rate = 192000
        self.shepard = shepard
        self.stream = sd.OutputStream(channels=1, samplerate=self.sample_rate, blocksize=0, dtype='float32', latency=0.1,
                                 callback=self.callback)

    def callback(self,outdata, frames, time, status):
        if status:
            print(status)
        #print(time.inputBufferAdcTime)
        #t = np.linspace(time.inputBufferAdcTime, time.inputBufferAdcTime + frames/self.sample_rate, frames)
        t = np.linspace(time.outputBufferDacTime, time.outputBufferDacTime + frames / self.sample_rate, frames)
        t,y =self.shepard.get_waveform(t)
        y /= y.max()
        outdata[:,0] = y

    def on(self):
        self.stream.start()

    def off(self):
        self.stream.stop()


