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
# SCANNER EINSTELLUNGEN
# ============================================================

st.sidebar.header("Scanner-Einstellungen")


rsi_min = st.sidebar.slider(
    "RSI Minimum",
    0,
    100,
    50
)


rsi_max = st.sidebar.slider(
    "RSI Maximum",
    0,
    100,
    70
)


volume_multiplier = st.sidebar.slider(
    "Volume Ratio Minimum",
    0.5,
    5.0,
    1.5,
    0.1
)


momentum_min = st.sidebar.slider(
    "Momentum Minimum (%)",
    -10.0,
    10.0,
    0.0,
    0.5
)


# ============================================================
# BACKTEST EINSTELLUNGEN
# ============================================================

st.sidebar.header("Backtest-Einstellungen")


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


initial_capital = st.sidebar.number_input(
    "Startkapital (€)",
    min_value=100.0,
    max_value=1000000.0,
    value=1000.0,
    step=100.0
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

                # Letzte vollständig abgeschlossene Kerze
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
# HALTEDAUER-VERGLEICH
# ============================================================

st.divider()

st.header("📈 Backtest – Vergleich der Haltedauer")

st.write(
    "Die Strategieparameter bleiben unverändert. "
    "Nur die Haltedauer wird verändert."
)


if st.button("5 Backtests starten"):

    holding_periods = [
        6,
        12,
        24,
        48,
        72
    ]

    comparison_results = []

    for holding_period in holding_periods:

        st.subheader(
            f"⏱️ Haltedauer: {holding_period} Stunden"
        )

        period_results = []

        for symbol in symbols:

            try:

                with st.spinner(
                    f"{symbol} – {holding_period} Stunden..."
                ):

                    df = get_ohlc(
                        symbol,
                        interval=60
                    )

                    trades, stats = run_backtest(
                        df,
                        holding_period=holding_period,
                        fee_per_side=fee_per_side,
                        slippage_per_side=slippage_per_side,
                        initial_capital=initial_capital,
                        rsi_min=rsi_min,
                        rsi_max=rsi_max,
                        volume_multiplier=volume_multiplier,
                        momentum_min=momentum_min
                    )

                    period_results.append({
                        "Haltedauer": holding_period,
                        "Coin": symbol,
                        "Trades": stats["trades"],
                        "Trefferquote %": stats["win_rate"],
                        "Ø Netto %": stats["average_profit"],
                        "Summe Netto %": stats["total_profit"],
                        "Startkapital €": stats["initial_capital"],
                        "Endkapital €": stats["final_capital"],
                        "Max Drawdown %": stats["max_drawdown"],
                        "Gebühren %": stats["total_fees"]
                    })

            except Exception as e:

                st.error(
                    f"Backtest-Fehler bei "
                    f"{symbol} ({holding_period}h): {e}"
                )

        if period_results:

            period_df = pd.DataFrame(
                period_results
            )

            st.dataframe(
                period_df,
                use_container_width=True,
                hide_index=True
            )

            comparison_results.extend(
                period_results
            )


    # ========================================================
    # GESAMTVERGLEICH
    # ========================================================

    if comparison_results:

        st.divider()

        st.header(
            "📊 Gesamtvergleich aller Haltedauern"
        )

        comparison_df = pd.DataFrame(
            comparison_results
        )

        st.dataframe(
            comparison_df,
            use_container_width=True,
            hide_index=True
        )


        # ----------------------------------------------------
        # SOL SPEZIELL
        # ----------------------------------------------------

        st.subheader(
            "🟣 SOL/USD – Haltedauervergleich"
        )

        sol_df = comparison_df[
            comparison_df["Coin"] == "SOL/USD"
        ].copy()

        st.dataframe(
            sol_df,
            use_container_width=True,
            hide_index=True
        )


        st.info(
            "Hinweis: Der Vergleich zeigt historische "
            "Simulationen. Eine bessere historische "
            "Performance bedeutet nicht automatisch "
            "eine bessere zukünftige Performance."
        )
