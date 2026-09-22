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
    Historischer Backtest.

    Jeder Trade verwendet das gesamte aktuelle Kapital.
    Gebühren und Slippage werden berücksichtigt.

    Der Backtest dient ausschließlich zur Simulation.
    """

    df = add_indicators(df)

    trades = []

    capital = initial_capital
    peak_capital = initial_capital
    max_drawdown_percent = 0.0

    last_index = len(df) - holding_period

    for i in range(last_index):

        row = df.iloc[i]

        signal = generate_signal(
            row,
            rsi_min=rsi_min,
            rsi_max=rsi_max,
            volume_multiplier=volume_multiplier,
            momentum_min=momentum_min
        )

        if not signal:
            continue

        entry_price = row["close"]

        exit_row = df.iloc[i + holding_period]

        exit_price = exit_row["close"]

        # Brutto-Rendite
        gross_profit_percent = (
            (exit_price - entry_price)
            / entry_price
        ) * 100

        # Gesamtkosten
        total_fee_percent = fee_per_side * 2

        total_slippage_percent = (
            slippage_per_side * 2
        )

        total_cost_percent = (
            total_fee_percent
            + total_slippage_percent
        )

        # Netto-Rendite
        net_profit_percent = (
            gross_profit_percent
            - total_cost_percent
        )

        capital_before = capital

        # Kapitalentwicklung
        capital = capital * (
            1 + net_profit_percent / 100
        )

        capital_after = capital

        # Höchststand aktualisieren
        if capital > peak_capital:
            peak_capital = capital

        # Drawdown berechnen
        drawdown_percent = (
            (capital - peak_capital)
            / peak_capital
        ) * 100

        if drawdown_percent < max_drawdown_percent:
            max_drawdown_percent = drawdown_percent

        trades.append({
            "Trade": len(trades) + 1,
            "Entry Time": row["timestamp"],
            "Entry Price": entry_price,
            "Exit Time": exit_row["timestamp"],
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

    trades_df = pd.DataFrame(trades)

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
