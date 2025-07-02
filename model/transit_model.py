import batman as bm
import numpy as np

def fit_transit_batman(time, flux, noise=0.0001):
    params = bm.TransitParams()
    params.t0 = 0
    params.per = 3
    params.rp = 0.1
    params.a = 15
    params.inc = 87
    params.ecc = 0
    params.w = 90
    params.limb_dark = "quadratic"
    params.u = [0.1, 0.3]

    model = bm.TransitModel(params, time)
    fit_flux = model.light_curve(params)
    chi2 = np.sum(((flux - fit_flux) / noise) ** 2)
    return fit_flux, chi2
