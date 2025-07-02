import numpy as np
import matplotlib.pyplot as plt
from taurex.parameter.parameterparser import ParameterParser
from astropy.io import fits


BIOSIGNATURE_LINES = {
    "H2O": [1.4, 6.2],
    "O2": [0.76],
    "O3": [9.6],
    "CH4": [3.3, 7.6],
    "CO2": [4.3, 15.0]
}

JWST_BANDPASSES = {
    "NIRSpec G140M": (1.0, 1.8),
    "NIRSpec G235H": (1.7, 3.1),
    "NIRSpec G395M": (2.9, 5.1),
    "MIRI LRS": (5.0, 12.0)
}

def run_taurex_spectrum(config_path="model/taurex_config.par"):
    parser = ParameterParser()
    parser.read(config_path)
    parser.setup_globals()
    model = parser.generate_appropriate_model()
    model.build()

    output = model.model()
    spec = output[0] if isinstance(output, (list, tuple)) else output
    spec = np.asarray(spec)

    wl = np.asarray(model.nativeWavenumberGrid)
    wl_um = (1e4 / wl) if wl[0] > 100 else wl

    return wl_um, spec

def estimate_transit_depth(wave_um, spectrum, Rp_Rs_ratio=0.1):
    depth_ppm = (Rp_Rs_ratio**2) * 1e6
    return wave_um, spectrum + depth_ppm

def get_biosignature_bands(selected_species):
    return [w for mol in selected_species for w in BIOSIGNATURE_LINES.get(mol, [])]

def inject_biosignature_overlay(ax, selected_species):
    band_lines = get_biosignature_bands(selected_species)
    for wl in band_lines:
        ax.axvline(wl, color="purple", linestyle=":", alpha=0.7)

def annotate_biosignatures(ax, selected_species):
    for mol in selected_species:
        for wl in BIOSIGNATURE_LINES.get(mol, []):
            ax.text(wl, ax.get_ylim()[1]*0.9, mol, color="purple", fontsize=9, rotation=90, ha="center")

def add_instrument_bandpasses(ax):
    for inst, (low, high) in JWST_BANDPASSES.items():
        ax.axvspan(low, high, color="lightgray", alpha=0.3, label=inst)
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc="upper right", fontsize=8)

def simulate_noise_floor(wave, spectrum, level='JWST'):
    rng = np.random.default_rng(seed=42)
    noise_ppm = 20 if level == "JWST" else 100
    noise = rng.normal(0, noise_ppm * 1e-6, size=len(spectrum))
    return spectrum + noise

def detect_biosignatures(wave_um, flux):
    scores = {}
    for mol, bands in BIOSIGNATURE_LINES.items():
        found = 0
        for band in bands:
            mask = np.abs(wave_um - band) < 0.05
            if mask.any():
                signal = flux[mask].mean()
                baseline = np.median(flux)
                contrast = np.abs(signal - baseline) / baseline
                if contrast > 0.005:
                    found += 1
        confidence = found / len(bands)
        scores[mol] = round(confidence, 3)
    return scores


def save_fits_spectrum(wave, flux, filename="flaretrace_output.fits"):
    col1 = fits.Column(name='WAVELENGTH', array=wave, format='E', unit='um')
    col2 = fits.Column(name='FLUX', array=flux, format='E', unit='ppm')
    cols = fits.ColDefs([col1, col2])

    hdu = fits.BinTableHDU.from_columns(cols)
    hdu.header['ORIGIN'] = 'FlareTrace'
    hdu.header['COMMENT'] = "Simulated exoplanet spectrum using TauREx"

    hdul = fits.HDUList([fits.PrimaryHDU(), hdu])
    hdul.writeto(filename, overwrite=True)
    return filename