import matplotlib.pyplot as plt

BIOSIGNATURE_LINES = {
    "H2O": 1.4,
    "O3": 9.6,
    "CH4": 3.3,
    "CO2": 4.3,
    "O2": 0.76
}

def plot_biosignature_overlay(wavelengths, flux):
    plt.plot(wavelengths, flux, label="Observed")
    for label, wl in BIOSIGNATURE_LINES.items():
        plt.axvline(x=wl, linestyle="--", alpha=0.5, label=label)
    plt.legend()
    plt.xlabel("Wavelength (μm)")
    plt.ylabel("Transit Depth / Flux")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
