from retrieval_runner import run_taurex_spectrum, run_platon

wl_t, flux_t = run_taurex_spectrum()
print("τREx WL (µm):", wl_t[:5])

wl_p, depth_p = run_platon(wl_t, flux_t)
print("Platon Depths:", depth_p[:5])
