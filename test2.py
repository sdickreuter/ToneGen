import sounddevice as sd
import numpy as np
square = np.ones(44100, dtype="int32") * 214748364
sd.play(square) # Results in static

square_floats = np.ones(44100, dtype="float32")
sd.play(square_floats) # results in "on" state