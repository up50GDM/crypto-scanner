import pandas as pd

from indicators import add_indicators
from signals import generate_signal


def run_backtest(
    df,
    holding_period=24,
    fee_per_side=0.40,
    slippage_per_side=0.0,
    initial_capital=1000.0,
    rsi_min=50,
    rsi_max=70,
    volume_multiplier=1.5,
    momentum_min=0.0
):
    """
    Historischer Backtest ohne überlappende Trades.

    Das Signal wird auf Basis einer abgeschlossenen Kerze erzeugt.
    Der Einstieg erfolgt erst zum Open der nächsten Kerze.

    Nach einem Einstieg wird die Position für die komplette
    Haltedauer gehalten. Während dieser Zeit werden neue Signale
    ignoriert.

    Gebühren und Slippage werden berücksichtigt.
    Der Backtest dient ausschließlich zur Simulation.
    """

    # ============================================================
    # INDIKATOREN BERECHNEN
    # ============================================================

    df = add_indicators(df)

    trades = []

    capital = initial_capital
    peak_capital = initial_capital
    max_drawdown_percent = 0.0

    i = 0

    # ============================================================
    # BACKTEST
    # ============================================================

    while i < len(df) - 1:

        # --------------------------------------------------------
        # Signal auf abgeschlossener Kerze
        # --------------------------------------------------------

        row = df.iloc[i]

        signal = generate_signal(
            row,
            rsi_min=rsi_min,
            rsi_max=rsi_max,
            volume_multiplier=volume_multiplier,
            momentum_min=momentum_min
        )

        if not signal:
            i += 1
            continue

        # --------------------------------------------------------
        # Einstieg erst bei der nächsten Kerze
        # --------------------------------------------------------

        entry_index = i + 1

        if entry_index >= len(df):
            break

        entry_row = df.iloc[entry_index]

        entry_price = entry_row["open"]
        entry_time = entry_row["timestamp"]

        # --------------------------------------------------------
        # Ausstieg nach der definierten Haltedauer
        # --------------------------------------------------------

        exit_index = entry_index + holding_period

        if exit_index >= len(df):
            break

        exit_row = df.iloc[exit_index]

        exit_price = exit_row["close"]
        exit_time = exit_row["timestamp"]

        # --------------------------------------------------------
        # Brutto-Ergebnis
        # --------------------------------------------------------

        gross_profit_percent = (
            (exit_price - entry_price)
            / entry_price
        ) * 100

        # --------------------------------------------------------
        # Gebühren
        # --------------------------------------------------------

        total_fee_percent = (
            fee_per_side * 2
        )

        # --------------------------------------------------------
        # Slippage
        # --------------------------------------------------------

        total_slippage_percent = (
            slippage_per_side * 2
        )

        # --------------------------------------------------------
        # Netto-Ergebnis
        # --------------------------------------------------------

        total_cost_percent = (
            total_fee_percent
            + total_slippage_percent
        )

        net_profit_percent = (
            gross_profit_percent
            - total_cost_percent
        )

        # --------------------------------------------------------
        # Kapitalentwicklung
        # --------------------------------------------------------

        capital_before = capital

        capital = capital * (
            1 + net_profit_percent / 100
        )

        capital_after = capital

        # --------------------------------------------------------
        # Drawdown
        # --------------------------------------------------------

        if capital > peak_capital:
            peak_capital = capital

        drawdown_percent = (
            (capital - peak_capital)
            / peak_capital
        ) * 100

        if drawdown_percent < max_drawdown_percent:
            max_drawdown_percent = drawdown_percent

        # --------------------------------------------------------
        # Trade speichern
        # --------------------------------------------------------

        trades.append({
            "Trade": len(trades) + 1,
            "Signal Time": row["timestamp"],
            "Entry Time": entry_time,
            "Entry Price": entry_price,
            "Exit Time": exit_time,
            "Exit Price": exit_price,
            "Holding Period": holding_period,
            "Gross Profit %": gross_profit_percent,
            "Fees %": total_fee_percent,
            "Slippage %": total_slippage_percent,
            "Net Profit %": net_profit_percent,
            "Capital Before": capital_before,
            "Capital After": capital_after,
            "Drawdown %": drawdown_percent
        })

        # --------------------------------------------------------
        # Keine überlappenden Trades
        # --------------------------------------------------------

        i = exit_index + 1

    # ============================================================
    # TRADES DATAFRAME
    # ============================================================

    trades_df = pd.DataFrame(trades)

    # ============================================================
    # KEINE TRADES
    # ============================================================

    if trades_df.empty:

        statistics = {
            "trades": 0,
            "win_rate": 0.0,
            "average_profit": 0.0,
            "total_profit": 0.0,
            "total_fees": 0.0,
            "initial_capital": initial_capital,
            "final_capital": initial_capital,
            "max_drawdown": 0.0
        }

        return trades_df, statistics

    # ============================================================
    # STATISTIKEN
    # ============================================================

    winning_trades = (
        trades_df["Net Profit %"] > 0
    ).sum()

    total_trades = len(trades_df)

    win_rate = (
        winning_trades / total_trades
    ) * 100

    average_profit = (
        trades_df["Net Profit %"].mean()
    )

    total_profit = (
        trades_df["Net Profit %"].sum()
    )

    total_fees = (
        trades_df["Fees %"].sum()
    )

    # ============================================================
    # STATISTIKEN ZUSAMMENSTELLEN
    # ============================================================

    statistics = {
        "trades": total_trades,
        "win_rate": win_rate,
        "average_profit": average_profit,
        "total_profit": total_profit,
        "total_fees": total_fees,
        "initial_capital": initial_capital,
        "final_capital": capital,
        "max_drawdown": max_drawdown_percent
    }

    return trades_df, statistics
