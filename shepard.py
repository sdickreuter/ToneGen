import numpy as np
import math

def _gauss(x, x0, sigma):
    return (1 / (sigma ** 2)) * np.exp(-(x-x0) ** 2 / sigma ** 2)


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

    def get_spectrum(self):
        buf = np.arange(1,self.n)
        x = buf*self.starting_freq


        x = np.linspace(0.0,self.starting_freq*(self.n+1),2000)
        y = np.zeros(len(x))
        for i in range(self.n):
            y += _gauss(x,(i+1)*self.starting_freq,0.1)

        if (self.n % 2) == 0:
            y *= _gauss(x,self.starting_freq+self.starting_freq*int(self.n/2)+self.envelope_x0,self.envelope_width)
        else:
            y *= _gauss(x,self.starting_freq+self.starting_freq*(int(self.n/2)+1)+self.envelope_x0,self.envelope_width)


        return x,y


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    s = ShepardTone(1.0,5,3.0,2.5)
    x,y = s.get_spectrum()
    plt.plot(x,y)
    plt.show()

