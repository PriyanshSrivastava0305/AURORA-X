# core/drift_detector.py
from etsi.watchdog import Monitor

def detect_drift(df, features=["flux", "flux_err"], window=300):
    df = df.set_index("datetime")
    monitor = Monitor(reference_df=df.iloc[:window])
    monitor.enable_logging("logs/rolling_log.csv")
    return monitor.watch_rolling(df, window=window, freq="H", features=features)
