import numpy as np

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
        self._calc_spectrum()

    def set(self, starting_freq, n, envelope_width, envelope_x0):
        self.starting_freq = starting_freq
        self.n = n
        self.envelope_width = envelope_width
        self.envelope_x0 = envelope_x0
        self._calc_spectrum()

    def _calc_spectrum(self):
        buf = np.arange(0, self.n)
        self.freqs = 2 ** buf * self.starting_freq

        x = np.arange(1, len(self.freqs)+1)
        self.amps = _gauss(x, self.n / 2 + self.envelope_x0, self.envelope_width)


    def get_waveform(self,t=None):

        if t is None:
            t = np.linspace(0,0.01,1000)
        y2 = np.zeros(len(t))
        for i in range(len(self.freqs)):
             y2 += np.sin(self.freqs[i]*(2*np.pi)*t)*self.amps[i]

        y2 /= y2.max()
        return t,y2

    def calc_fft(self,x,y):
        #x2 = np.fft.fftfreq(len(self.y), d=1./len(self.x))
        x2 = np.fft.rfftfreq(len(y), d=np.diff((x))[0])
        y2 = abs(np.real(np.fft.rfft(y)))

        return x2,y2




if __name__ == '__main__':
    import matplotlib.pyplot as plt
    s = ShepardTone(1.0,10,1.0,0.0)

    x,y = s.get_waveform()
    print(x)
    print(y)
    plt.plot(x,y)
    plt.show()

    x,y = s.calc_fft(x,y)
    print(x)
    print(y)
    plt.plot(x,y)
    plt.show()

