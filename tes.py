from lightkurve import search_lightcurve
lc = search_lightcurve("Kepler-8", mission="Kepler").download_all().stitch()
lc.plot()
print('done')