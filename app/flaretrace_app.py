import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from core.retrieval_runner import (
    run_taurex_spectrum,
    estimate_transit_depth,
    inject_biosignature_overlay,
    annotate_biosignatures,
    add_instrument_bandpasses,
    simulate_noise_floor,
    detect_biosignatures,
    save_fits_spectrum,
)

from core.lightcurve_tools import load_real_lightcurve, phase_fold_lc
from model.transit_model import fit_transit_batman

# -------------------- Streamlit UI Setup --------------------
st.set_page_config(page_title="FlareTrace: Exoplanet Atmospheres", layout="wide")
st.title("☄️ FlareTrace: NASA-Grade Exoplanet Atmosphere Viewer")
st.markdown("**Mission-Ready**: TauREx modeling, JWST overlays, biosignature detection, and real LC fitting.")

# -------------------- Sidebar --------------------
with st.sidebar:
    st.header("🔧 Configuration")

    config_path = st.text_input("TauREx Config File", value="model/taurex_config.par")
    rp_rs = st.slider("Rp / Rs", 0.01, 0.2, 0.1, 0.005)

    selected_species = st.multiselect(
        "Highlight Biosignatures", ["H2O", "O2", "O3", "CH4", "CO2"],
        default=["H2O", "O2", "CH4"]
    )
    inject_noise = st.checkbox("Add JWST Noise Floor")
    overlay_toggle = st.checkbox("Show (Rp/Rs)² Transit Overlay")
    show_bandpasses = st.checkbox("Show JWST Instrument Bandpasses")

    st.markdown("---")
    st.header("📡 Light Curve Parameters")
    target = st.text_input("Target (Kepler/K2/TESS)", value="Kepler-10")
    mission = st.selectbox("Mission", ["Kepler", "TESS"], index=0)
    period = st.number_input("Orbital Period (days)", value=3.0)
    t0 = st.number_input("Epoch Time (T0)", value=0.0)

    run_all = st.button("🚀 Run Full Pipeline")

# -------------------- Main Pipeline --------------------
if run_all:
    # ----- TauREx -----
    with st.spinner("Running TauREx..."):
        try:
            wave_um, flux = run_taurex_spectrum(config_path)
            if inject_noise:
                flux = simulate_noise_floor(wave_um, flux)
        except Exception as e:
            st.error(f"TauREx failed: {e}")
            st.stop()

    wave_overlay, flux_overlay = estimate_transit_depth(wave_um, flux, rp_rs)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(wave_um, flux, label="TauREx Spectrum", lw=2)

    if overlay_toggle:
        ax.plot(wave_overlay, flux_overlay, "--", label=f"(Rp/Rs)² ≈ {rp_rs**2:.4f}", color="orange")

    inject_biosignature_overlay(ax, selected_species)
    annotate_biosignatures(ax, selected_species)

    if show_bandpasses:
        add_instrument_bandpasses(ax)

    ax.set_xlabel("Wavelength (µm)")
    ax.set_ylabel("Transit Depth / Flux")
    ax.set_title("Simulated Transmission Spectrum")
    ax.grid(True)
    ax.legend()

    st.subheader("📈 Transmission Spectrum")
    st.pyplot(fig)

    fits_path = save_fits_spectrum(wave_um, flux)
    with open(fits_path, "rb") as f:
        st.download_button(
            label="📥 Download FITS File",
            data=f,
            file_name="flaretrace_output.fits",
            mime="application/fits"
        )

    # ----- Biosignature Confidence Matrix -----
    st.subheader("🧬 Biosignature Confidence Matrix")
    try:
        scores = detect_biosignatures(wave_um, flux)
        if scores:
            df = pd.DataFrame.from_dict(scores, orient="index", columns=["Confidence"])
            df["Confidence (%)"] = (df["Confidence"] * 100).round(1)
            st.dataframe(df.style.background_gradient(cmap="YlGnBu", subset=["Confidence (%)"]))
        else:
            st.info("No biosignatures detected.")
    except Exception as e:
        st.error(f"Biosignature detection failed: {e}")

    # ----- Real Light Curve Fitting -----
    st.subheader("🔭 Kepler/TESS Light Curve Fitting")
    st.caption(f"Target: **{target}**, Mission: **{mission}**, Period: **{period} days**, T₀: **{t0}**")
    try:
        st.write("Loading light curve...")
        lc = load_real_lightcurve(target, mission)
        folded = phase_fold_lc(lc, period, t0)

        st.subheader("🌀 Phase-Folded Light Curve")
        st.pyplot(folded.plot().figure)

        fc, chi2 = fit_transit_batman(folded.time.value, folded.flux.value)
        st.write(f"Transit Fit χ² = {chi2:.2f}")

        fig2, ax2 = plt.subplots()
        ax2.scatter(folded.time.value, folded.flux.value, s=5, alpha=0.4, label="Observed")
        ax2.plot(folded.time.value, fc, 'r-', label="Batman Fit")
        ax2.set(xlabel="Phase", ylabel="Flux")
        ax2.grid(True)
        ax2.legend()
        st.pyplot(fig2)

    except Exception as e:
        st.error(f"Light curve loading or fitting failed: {e}")

    # ----- Final Summary -----
    st.markdown(
        f"""
        ### ✅ Mission Summary
        - Forward Model: **TauREx**
        - Config: `{config_path}`
        - Target: `{target}` ({mission})
        - Biosignatures: **{", ".join(selected_species) if selected_species else "None"}**
        - Rp/Rs² Overlay: {"✅ Yes" if overlay_toggle else "❌ No"}
        - JWST Bandpasses: {"✅ Yes" if show_bandpasses else "❌ No"}
        - Noise Simulation: {"✅ Yes" if inject_noise else "❌ No"}
        """
    )
