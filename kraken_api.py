import requests
import pandas as pd


KRAKEN_URL = "https://api.kraken.com/0/public/OHLC"


def get_ohlc(symbol="BTC/USD", interval=60):
    """
    Holt OHLC-Daten von Kraken.

    interval:
        1   = 1 Minute
        5   = 5 Minuten
        15  = 15 Minuten
        30  = 30 Minuten
        60  = 1 Stunde
        240 = 4 Stunden
        1440 = 1 Tag
    """

    params = {
        "pair": symbol,
        "interval": interval
    }

    response = requests.get(
        KRAKEN_URL,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    if data["error"]:
        raise RuntimeError(
            f"Kraken API Fehler: {data['error']}"
        )

    result = data["result"]

    # Kraken liefert neben den Kerzendaten
    # auch einen "last"-Wert.
    pair_keys = [
        key for key in result
        if key != "last"
    ]

    if not pair_keys:
        raise RuntimeError(
            "Keine Marktdaten von Kraken erhalten."
        )

    candles = result[pair_keys[0]]

    columns = [
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "vwap",
        "volume",
        "count"
    ]

    df = pd.DataFrame(
        candles,
        columns=columns
    )

    # Zeit umwandeln
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        unit="s"
    )

    # Zahlenfelder umwandeln
    numeric_columns = [
        "open",
        "high",
        "low",
        "close",
        "vwap",
        "volume"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    return df


if __name__ == "__main__":

    df = get_ohlc(
        "BTC/USD",
        60
    )

    print(df.tail())
