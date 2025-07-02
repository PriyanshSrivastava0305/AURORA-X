# core/jwst_parser.py
from astropy.io import fits
import pandas as pd

def parse_jwst_fits(file_path):
    with fits.open(file_path) as hdul:
        flux = hdul[1].data['FLUX']
        wave = hdul[1].data['WAVELENGTH']
    return pd.DataFrame({"wavelength": wave, "flux": flux})
