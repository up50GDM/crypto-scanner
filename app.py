import streamlit as st
import pandas as pd

from kraken_api import get_ohlc
from indicators import add_indicators
from signals import generate_signal
from backtest import run_backtest


st.set_page_config(
    page_title="Crypto Scanner",
    page_icon="📊",
    layout="wide"
)


st.title("📊 Crypto Scanner")

st.write(
    "Markt-Scanner und historischer Backtest "
    "für BTC, ETH, SOL und XRP."
)


# ============================================================
# EINSTELLUNGEN
# ============================================================

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


# ============================================================
# BACKTEST EINSTELLUNGEN
# ============================================================

st.sidebar.header("Backtest-Einstellungen")


holding_period = st.sidebar.selectbox(
    "Haltedauer",
    options=[12, 24, 48, 72],
    index=1
)


fee_per_side = st.sidebar.number_input(
    "Gebühr pro Seite (%)",
    min_value=0.0,
    max_value=2.0,
    value=0.40,
    step=0.01
)


slippage_per_side = st.sidebar.number_input(
    "Slippage pro Seite (%)",
    min_value=0.0,
    max_value=2.0,
    value=0.0,
    step=0.01
)


symbols = [
    "BTC/USD",
    "ETH/USD",
    "SOL/USD",
    "XRP/USD"
]


# ============================================================
# AKTUELLER SCAN
# ============================================================

st.header("🔍 Aktueller Markt-Scan")


if st.button("Scan starten"):

    results = []

    with st.spinner("Marktdaten werden geladen..."):

        for symbol in symbols:

            try:

                df = get_ohlc(
                    symbol,
                    interval=60
                )

                df = add_indicators(df)

                # Letzte vollständige Kerze
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
                    "Signal": (
                        "🟢 WATCHLIST"
                        if signal
                        else "⚪"
                    )
                })

            except Exception as e:

                st.error(
                    f"Fehler bei {symbol}: {e}"
                )

    if results:

        result_df = pd.DataFrame(results)

        st.subheader("Marktübersicht")

        st.dataframe(
            result_df,
            use_container_width=True,
            hide_index=True
        )


        watchlist = result_df[
            result_df["Signal"] == "🟢 WATCHLIST"
        ]

        st.subheader("⭐ Watchlist")


        if watchlist.empty:

            st.info(
                "Momentan erfüllt kein Coin "
                "alle Kriterien."
            )

        else:

            st.success(
                f"{len(watchlist)} Coin(s) "
                "erfüllen momentan alle Kriterien."
            )

            st.dataframe(
                watchlist,
                use_container_width=True,
                hide_index=True
            )


# ============================================================
# BACKTEST
# ============================================================

st.divider()

st.header("📈 Historischer Backtest")


st.write(
    "Der Backtest simuliert vergangene Signale "
    "mit einer festen Haltedauer und berücksichtigt "
    "Gebühren sowie optionale Slippage."
)


if st.button("Backtest starten"):

    backtest_results = []

    with st.spinner(
        "Historische Marktdaten werden geladen "
        "und getestet..."
    ):

        for symbol in symbols:

            try:

                df = get_ohlc(
                    symbol,
                    interval=60
                )

                trades, statistics = run_backtest(
                    df,
                    holding_period=holding_period,
                    fee_per_side=fee_per_side,
                    slippage_per_side=slippage_per_side,
                    rsi_min=rsi_min,
                    rsi_max=rsi_max,
                    volume_multiplier=volume_multiplier,
                    momentum_min=momentum_min
                )

                backtest_results.append({
                    "Coin": symbol,
                    "Trades": statistics["trades"],
                    "Trefferquote %": statistics["win_rate"],
                    "Ø Netto-Ergebnis %": statistics[
                        "average_profit"
                    ],
                    "Summe Netto %": statistics[
                        "total_profit"
                    ],
                    "Gebühren %": statistics[
                        "total_fees"
                    ]
                })

            except Exception as e:

                st.error(
                    f"Backtest-Fehler bei {symbol}: {e}"
                )


    if backtest_results:

        backtest_df = pd.DataFrame(
            backtest_results
        )

        st.subheader("Backtest-Ergebnisse")

        st.dataframe(
            backtest_df,
            use_container_width=True,
            hide_index=True
        )


        st.info(
            "Die Ergebnisse sind historische Simulationen "
            "und keine Garantie für zukünftige Ergebnisse."
        )
