import pandas as pd


def calculate_rsi(close, period=14):
    """Berechnet den RSI."""

    delta = close.diff()

    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)

    average_gain = gains.ewm(
        alpha=1 / period,
        adjust=False
    ).mean()

    average_loss = losses.ewm(
        alpha=1 / period,
        adjust=False
    ).mean()

    rs = average_gain / average_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi


def calculate_average_volume(volume, period=20):
    """Berechnet den gleitenden Volumendurchschnitt."""

    return volume.rolling(
        window=period
    ).mean()


def calculate_volume_ratio(volume, period=20):
    """Vergleicht aktuelles Volumen mit dem Durchschnitt."""

    average_volume = calculate_average_volume(
        volume,
        period
    )

    return volume / average_volume


def calculate_momentum(close, period=5):
    """Berechnet die prozentuale Preisveränderung."""

    return close.pct_change(
        periods=period
    ) * 100


def add_indicators(df):
    """Fügt alle Indikatoren zum DataFrame hinzu."""

    df = df.copy()

    df["rsi"] = calculate_rsi(
        df["close"],
        14
    )

    df["average_volume"] = calculate_average_volume(
        df["volume"],
        20
    )

    df["volume_ratio"] = calculate_volume_ratio(
        df["volume"],
        20
    )

    df["momentum"] = calculate_momentum(
        df["close"],
        5
    )

    return df
