import streamlit as st
import pandas as pd

from kraken_api import get_ohlc
from indicators import add_indicators
from signals import generate_signal


st.set_page_config(
    page_title="Crypto Scanner",
    page_icon="📊",
    layout="wide"
)


st.title("📊 Crypto Scanner")
st.write("Markt-Scanner für BTC, ETH, SOL und XRP")


# Einstellungen
st.sidebar.header("Scanner-Einstellungen")

rsi_min = st.sidebar.slider(
    "RSI Minimum",
    min_value=0,
    max_value=100,
    value=50
)

rsi_max = st.sidebar.slider(
    "RSI Maximum",
    min_value=0,
    max_value=100,
    value=70
)

volume_multiplier = st.sidebar.slider(
    "Volume Ratio Minimum",
    min_value=0.5,
    max_value=5.0,
    value=1.5,
    step=0.1
)

momentum_min = st.sidebar.slider(
    "Momentum Minimum (%)",
    min_value=-10.0,
    max_value=10.0,
    value=0.0,
    step=0.5
)


symbols = [
    "BTC/USD",
    "ETH/USD",
    "SOL/USD",
    "XRP/USD"
]


# Scanner starten
if st.button("🔍 Scan starten"):

    results = []

    with st.spinner("Marktdaten werden geladen..."):

        for symbol in symbols:

            try:
                df = get_ohlc(symbol, interval=60)
                df = add_indicators(df)

                # Letzte vollständige Kerze verwenden
                latest = df.iloc[-2]

                signal = generate_signal(
                    latest,
                    rsi_min=rsi_min,
                    rsi_max=rsi_max,
                    volume_multiplier=volume_multiplier,
                    momentum_min=momentum_min
                )

                results.append({
                    "Coin": symbol,
                    "Zeit": latest["timestamp"],
                    "Preis": latest["close"],
                    "RSI": latest["rsi"],
                    "Volume Ratio": latest["volume_ratio"],
                    "Momentum %": latest["momentum"],
                    "Signal": "🟢 WATCHLIST" if signal else "⚪"
                })

            except Exception as e:

                st.error(
                    f"Fehler bei {symbol}: {e}"
                )


    # Ergebnisse anzeigen
    if results:

        result_df = pd.DataFrame(results)

        st.subheader("Marktübersicht")

        st.dataframe(
            result_df,
            use_container_width=True,
            hide_index=True
        )


        # Watchlist
        watchlist = result_df[
            result_df["Signal"] == "🟢 WATCHLIST"
        ]

        st.subheader("⭐ Watchlist")


        if watchlist.empty:

            st.info(
                "Momentan erfüllt kein Coin alle Kriterien."
            )

        else:

            st.success(
                f"{len(watchlist)} Coin(s) erfüllen momentan alle Kriterien."
            )

            st.dataframe(
                watchlist,
                use_container_width=True,
                hide_index=True
            )
