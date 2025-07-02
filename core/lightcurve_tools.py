# core/lightcurve_tools.py

import os
import shutil
from lightkurve import search_lightcurve

def load_real_lightcurve(target, mission="Kepler"):
    """Fetch and clean light curve. Auto-clears corrupted cache files."""
    try:
        lc = search_lightcurve(target, mission=mission).download_all().stitch().remove_nans().normalize()
        return lc
    except Exception as e:
        # Attempt to clear corrupted cache
        cache_dir = os.path.expanduser("~/.lightkurve/cache")
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir, ignore_errors=True)
        raise RuntimeError(f"Corrupted cache. Deleted local files. Try again. Original error: {e}")

def phase_fold_lc(lc, period, t0):
    """Return phase-folded light curve."""
    folded = lc.fold(period=period, epoch_time=t0)
    return folded
