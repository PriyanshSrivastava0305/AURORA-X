# core/retrieval_runner.py

from taurex.parameter.parameterparser import ParameterParser
from platon.transit_depth_calculator import TransitDepthCalculator
from platon.constants import R_jup, M_jup, R_sun
import numpy as np

def run_taurex_spectrum(config_path="model/taurex_config.par"):
    """
    Loads and builds a TauREx forward model using ParameterParser.
    Returns wavelength in microns and spectrum.
    """
    parser = ParameterParser()
    parser.read(config_path)
    parser.setup_globals()
    model = parser.generate_appropriate_model()
    model.build()
    # spec = model.model()
    # if isinstance(spec, (list, tuple)) and isinstance(spec[0], (list, np.ndarray)):
    #     spec = np.array(spec[0])  # Take the first output if multiple are returned
    # else:
    #     spec = np.array(spec)

    # wl = model.nativeWavenumberGrid
    # # Convert from wavenumber (cm-1) to microns if needed:
    # # TauREx grid is in wavenumber; convert: λ (µm) = 1e4 / wngrid
    # if isinstance(wl[0], (int, float)) and wl[0] > 100:  # likely cm⁻¹
    #     wl_um = 1e4 / np.array(wl)
    # else:
    #     wl_um = np.array(wl)
    # return wl_um, np.array(spec)

        # Run TauREx forward model
    output = model.model()

    # TauREx might return (flux,) or (flux, error), or more — handle gracefully
    if isinstance(output, (list, tuple)):
        spec = output[0]  # Take the primary flux output
    else:
        spec = output

    # Ensure it's a proper NumPy array
    spec = np.asarray(spec)

    # Get wavelength grid (TauREx uses wavenumber in cm⁻¹)
    wl = model.nativeWavenumberGrid
    wl = np.asarray(wl)

    # Convert to microns if in wavenumber
    if wl[0] > 100:  # cm⁻¹, assume it's wavenumber
        wl_um = 1e4 / wl
    else:
        wl_um = wl

    return wl_um, spec


def run_platon(wave_um, flux, star_r=1.0, planet_r=1.0, planet_m=1.0, temp=1000):
    """
    Runs PLATON transit depth calculator on TauREx output.
    Returns wavelengths in microns and transit depth.
    """
    calc = TransitDepthCalculator()
    wave_m = wave_um * 1e-6
    w_m, depths, info = calc.compute_depths(
        R_sun * star_r,
        M_jup * planet_m,
        R_jup * planet_r,
        temp,
        wavelengths=wave_m,
        full_output=True
    )
    return w_m * 1e6, depths
