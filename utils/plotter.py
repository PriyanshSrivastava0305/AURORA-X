import numpy as np
import matplotlib.pyplot as plt

data = np.loadtxt("model/h2o_spectrum.txt")
wl, depth = data[:, 0], data[:, 1]

plt.plot(wl, depth)
plt.xlabel("Wavelength (µm)")
plt.ylabel("Transit depth")
plt.title("TauREx Transmission Spectrum (H₂O)")
plt.grid(True)
plt.show()
