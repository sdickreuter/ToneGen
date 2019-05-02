import numpy as np

def _gauss(x, x0, sigma):
    #return (1 / (sigma ** 2)) * np.exp(-(x-x0) ** 2 / sigma ** 2)
    return np.exp(-(x-x0) ** 2 / sigma ** 2)


class ShepardTone(object):

    def __init__(self, starting_freq, n, envelope_width, envelope_x0, volume, low_cutoff, high_cutoff):
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
        self.volume = volume
        self.low_cutoff = low_cutoff
        self.high_cutoff = high_cutoff
        self._calc_spectrum()

    def set(self, starting_freq, n, envelope_width, envelope_x0, volume, low_cutoff, high_cutoff):
        self.starting_freq = starting_freq
        self.n = n
        self.envelope_width = envelope_width
        self.envelope_x0 = envelope_x0
        self.volume = volume
        self.low_cutoff = low_cutoff
        self.high_cutoff = high_cutoff
        self._calc_spectrum()

    def _calc_spectrum(self):
        self.freqs = np.zeros(self.n, dtype=np.float32)
        for i in range(self.n):
            self.freqs[i] = 2**i * self.starting_freq

        if self.n > 1:
            ind = self.freqs >= self.low_cutoff
            self.freqs = self.freqs[ind]

            ind = self.freqs <= self.high_cutoff
            freqs = self.freqs[ind]

            self.n = len(freqs)

        x = np.arange(1, len(self.freqs)+1,dtype=np.float32)
        self.amps = _gauss(x, self.n / 2 + self.envelope_x0, self.envelope_width)



    def get_waveform(self,t):
        y2 = np.zeros(len(t))
        for i in range(len(self.freqs)):
             y2 += np.sin(self.freqs[i]*(2*np.pi)*t)*self.amps[i]

        y2 /= y2.max()
        y2 *= self.volume
        return y2

    def get_freqs(self):
        return self.freqs

    def get_amps(self):
        return self.amps


    def get_starting_freq(self):
        return self.starting_freq

    def get_n(self):
        return self.n

    def get_envelope_width(self):
        return self.envelope_width

    def get_envelope_x0(self):
        return self.envelope_x0

    def get_low_cutoff(self):
        return self.low_cutoff

    def get_high_cutoff(self):
        return self.high_cutoff

    def get_volume(self):
        return self.volume


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

