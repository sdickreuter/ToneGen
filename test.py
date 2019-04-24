import sounddevice as sd
import numpy as np


# calculate note frequencies
A_freq = 440
Csh_freq = A_freq * 2 ** (4 / 12)
E_freq = A_freq * 2 ** (7 / 12)

# get timesteps for each sample, T is note duration in seconds
#sample_rate = 44100
sample_rate = 192000 # 44100
T = 1.0

def gen_sound(time,frames):
    pass

duration = 3*T  # seconds

def dump(obj):
  for attr in dir(obj):
    print("obj.%s = %r" % (attr, getattr(obj, attr)))

def callback(outdata, frames, time, status):
    if status:
        print(status)
    dump(time)
    #print(time.inputBufferAdcTime)
    #print(time.inputBufferAdcTime + frames/sample_rate)
    t = np.linspace(time.outputBufferDacTime, time.outputBufferDacTime + frames/sample_rate, frames)
    if time.inputBufferAdcTime < T:
        audio = np.sin(A_freq * t * 2 * np.pi)
    elif time.inputBufferAdcTime < T*2:
        audio = np.sin(Csh_freq * t * 2 * np.pi)
    elif time.inputBufferAdcTime < T*3:
        audio = np.sin(E_freq * t * 2 * np.pi)

    #audio *= 32767 / np.max(np.abs(audio))
    #audio = audio.astype(np.int16)
    #audio *= 2147483647 / np.max(np.abs(audio))
    #audio = audio.astype(np.int32)
    outdata[:,0] = audio

stream = sd.OutputStream(channels=1, samplerate=sample_rate,blocksize=0 ,dtype='float32',latency=0.1, callback=callback)
stream.start()
sd.sleep(int(duration * 1000))
stream.close()

