import numpy as np

cimport numpy as np
from libc.math cimport exp, sin, pi
cimport cython

@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
cdef float[:] _gauss(float[:] x, float x0, float sigma):
    cdef float[:] res = np.empty(len(x),dtype=np.float32)
    cdef int i = 0
    for i in range(len(x)):
        res[i] = exp(-(x[i] - x0) ** 2 / sigma ** 2)
    return res


cdef class ShepardTone:
    cdef float starting_freq
    cdef int n
    cdef float envelope_width
    cdef float envelope_x0
    cdef float[:] freqs
    cdef float[:] amps
    cdef float low_cutoff
    cdef float high_cutoff

    def __init__(self, float starting_freq, int n, float envelope_width, float envelope_x0, float low_cutoff = -1.0, float high_cutoff=-1.0):
        self.starting_freq = starting_freq
        self.n = n
        self.envelope_width = envelope_width
        self.envelope_x0 = envelope_x0
        self.low_cutoff = low_cutoff
        self.high_cutoff = high_cutoff
        self._calc_spectrum()


    def set(self, float starting_freq, int n, float envelope_width, float envelope_x0, float low_cutoff = -1.0, float high_cutoff=-1.0):
        self.starting_freq = starting_freq
        self.n = n
        self.envelope_width = envelope_width
        self.envelope_x0 = envelope_x0
        self.low_cutoff = low_cutoff
        self.high_cutoff = high_cutoff
        self._calc_spectrum()


    @cython.boundscheck(False)  # Deactivate bounds checking
    @cython.wraparound(False)   # Deactivate negative indexing.
    def _calc_spectrum(self):
        self.freqs = np.zeros(self.n,dtype=np.float32)
        self.amps = np.zeros(self.n,dtype=np.float32)
        cdef int i = 0
        for i in range(self.n):
            self.freqs[i] = 2**i * self.starting_freq

             
        cdef float[:] x = np.arange(1, self.n + 1,dtype=np.float32)
        self.amps = _gauss(x, self.n / 2 + self.envelope_x0, self.envelope_width)


    @cython.boundscheck(False)  # Deactivate bounds checking
    @cython.wraparound(False)   # Deactivate negative indexing.
    def get_waveform(self, float[:] t):
        y = np.zeros(len(t),dtype=np.float32)
        cdef float[:] y2 = y

        cdef int i = 0
        cdef int f = 0
        for f in range(self.n):
            for i in range(len(t)):
                y2[i] += sin(self.freqs[f]*(2*pi)*t[i])*self.amps[f]

        for i in range(len(t)):
            y2[i] /= self.n

        #y /= y.max()
        return y

    def get_freqs(self):
        return self.freqs

    def get_amps(self):
        return self.amps






# class ShepardTone(object):

#     def __init__(self, starting_freq, n, envelope_width, envelope_x0):
#         self.starting_freq = starting_freq
#         self.n = n
#         self.envelope_width = envelope_width
#         self.envelope_x0 = envelope_x0
#         self.freqs = None
#         self.amps = None
#         self._calc_spectrum()

#     def set(self, starting_freq, n, envelope_width, envelope_x0):
#         self.starting_freq = starting_freq
#         self.n = n
#         self.envelope_width = envelope_width
#         self.envelope_x0 = envelope_x0
#         self._calc_spectrum()

#     def _calc_spectrum(self):
#         buf = np.arange(0, self.n)
#         self.freqs = 2 ** buf * self.starting_freq

#         x = np.arange(1, len(self.freqs)+1)
#         self.amps = _gauss(x, self.n / 2 + self.envelope_x0, self.envelope_width)


#     def get_waveform(self,t=None):

#         if t is None:
#             t = np.linspace(0,0.01,1000)
#         y2 = np.zeros(len(t))
#         for i in range(len(self.freqs)):
#              y2 += np.sin(self.freqs[i]*(2*np.pi)*t)*self.amps[i]

#         y2 /= y2.max()
#         return t,y2

#     def calc_fft(self,x,y):
#         #x2 = np.fft.fftfreq(len(self.y), d=1./len(self.x))
#         x2 = np.fft.rfftfreq(len(y), d=np.diff((x))[0])
#         y2 = abs(np.real(np.fft.rfft(y)))

#         return x2,y2




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

