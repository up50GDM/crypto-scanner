import pandas as pd

from indicators import add_indicators
from signals import generate_signal


def run_backtest(
    df,
    holding_period=24,
    fee_per_side=0.40,
    slippage_per_side=0.0,
    rsi_min=50,
    rsi_max=70,
    volume_multiplier=1.5,
    momentum_min=0.0
):
    """
    Führt einen einfachen historischen Backtest durch.

    Einstieg:
    Schlusskurs der Signal-Kerze.

    Ausstieg:
    Schlusskurs nach der definierten Anzahl von Kerzen.

    fee_per_side:
        Handelsgebühr pro Seite in Prozent.
        Beispiel: 0.40 bedeutet 0.40 % beim Kauf
        und 0.40 % beim Verkauf.

    slippage_per_side:
        Angenommene Slippage pro Seite in Prozent.
    """

    df = add_indicators(df)

    trades = []

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

        # Gebühren + Slippage
        total_cost_percent = (
            fee_per_side
            + fee_per_side
            + slippage_per_side
            + slippage_per_side
        )

        # Netto-Rendite
        net_profit_percent = (
            gross_profit_percent
            - total_cost_percent
        )

        trades.append({
            "Entry Time": row["timestamp"],
            "Entry Price": entry_price,
            "Exit Time": exit_row["timestamp"],
            "Exit Price": exit_price,
            "Holding Period": holding_period,
            "Gross Profit %": gross_profit_percent,
            "Fees %": fee_per_side * 2,
            "Slippage %": slippage_per_side * 2,
            "Net Profit %": net_profit_percent
        })

    trades_df = pd.DataFrame(trades)

    if trades_df.empty:

        return trades_df, {
            "trades": 0,
            "win_rate": 0.0,
            "average_profit": 0.0,
            "total_profit": 0.0,
            "total_fees": 0.0
        }

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
        "total_fees": total_fees
    }

    return trades_df, statistics
