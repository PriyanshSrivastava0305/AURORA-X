def apply_cloud_model(spectrum_df, cloud=True, haze=False):
    corrected = spectrum_df.copy()
    factor = 1.05 if cloud else 1.0
    if haze:
        factor *= 1.03
    corrected["corrected_flux"] = corrected["flux"] / factor
    return corrected
