import pandas as pd


def generate_signal(
    row,
    rsi_min=50,
    rsi_max=70,
    volume_multiplier=1.5,
    momentum_min=0.0
):
    """
    Prüft, ob eine Kerze alle definierten Signalbedingungen erfüllt.
    """

    if pd.isna(row["rsi"]):
        return False

    if pd.isna(row["volume_ratio"]):
        return False

    if pd.isna(row["momentum"]):
        return False

    rsi_ok = rsi_min <= row["rsi"] <= rsi_max
    volume_ok = row["volume_ratio"] >= volume_multiplier
    momentum_ok = row["momentum"] > momentum_min

    return rsi_ok and volume_ok and momentum_ok
