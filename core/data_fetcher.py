import pandas as pd
import numpy as np
from astropy.io import fits
from astropy.time import Time

def load_jwst_fits(filepath: str) -> pd.DataFrame:
    with fits.open(filepath) as hdul:
        data = hdul["SCI"].data
        header = hdul["SCI"].header
        wave = data["WAVELENGTH"]
        flux = data["FLUX"]
        dq = data["DQ"]

    df = pd.DataFrame({
        "wavelength": wave,
        "flux": flux,
        "dq": dq
    })
    df.dropna(inplace=True)
    return df
