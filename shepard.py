import numpy as np
import math

def _gauss(x, x0, sigma):
    #return (1 / (sigma ** 2)) * np.exp(-(x-x0) ** 2 / sigma ** 2)
    return np.exp(-(x-x0) ** 2 / sigma ** 2)


class ShepardTone(object):

    def __init__(self, starting_freq, n, envelope_width, envelope_x0):
        self.starting_freq = starting_freq
        self.n = n
        self.envelope_width = envelope_width
        self.envelope_x0 = envelope_x0
        #print(self.starting_freq)
        #print(self.n)
        #print(self.envelope_width)
        #print(self.envelope_x0)
        self.freqs = None
        self.amps = None

    def calc_spectrum(self):
        buf = np.arange(0,self.n)
        self.freqs = 2**buf *self.starting_freq

        if (self.n % 2) == 0:
            self.amps = _gauss(self.freqs,self.starting_freq*(int(self.n/2))+self.envelope_x0,self.envelope_width)
        else:
            self.amps = _gauss(self.freqs,self.starting_freq+self.starting_freq*(int(self.n/2))+self.envelope_x0,self.envelope_width)

    def get_waveform(self):

        x2 = np.linspace(0,1.0,2000)
        y2 = np.zeros(len(x2))
        for i in range(len(self.freqs)):
            f = self.freqs[i]
            a = self.amps[i]
            y2 += np.sin(f*(2*np.pi)*x2)*a

        return x2,y2

    def calc_fft(self,x,y):
        #x2 = np.fft.fftfreq(len(self.y), d=1./len(self.x))
        x2 = np.fft.rfftfreq(len(y), d=np.diff((x))[0])
        y2 = np.abs(np.real(np.fft.rfft(y)))

        return x2,y2



if __name__ == '__main__':
    import matplotlib.pyplot as plt
    s = ShepardTone(1.0,10,1.0,0.0)
    s.calc_spectrum()

    x,y = s.get_waveform()
    print(x)
    print(y)
    plt.plot(x,y)
    plt.show()

    x,y = s.calc_fft(y)
    print(x)
    print(y)
    plt.plot(x,y)
    plt.show()

