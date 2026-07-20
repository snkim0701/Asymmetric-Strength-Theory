"""
merge_loader.py
===============================

Merge price data and trading-flow data
into one standardized HDSDM dataset.

Author : HDSDM Project
Version: V1.4
"""
from __future__ import annotations

import pandas as pd

from src.loader.price_loader import load_price
from src.loader.flow_loader import load_flow


def load_dataset(
    ticker: str,
    start: str,
    end: str,
) -> pd.DataFrame:  
    """
    Load and merge HDSDM dataset.
    """

    # -------------------------
    # Load
    # -------------------------

    price = load_price(
        ticker=ticker,
        start=start,
        end=end,
    )

    flow = load_flow(
        ticker=ticker,
        start=start,
        end=end,
        max_pages=40,
    )

    #-------------------------
    # Validate
    #-------------------------
    if price.empty:
        raise ValueError(
            f"No price data for {ticker} "
            f"({start} ~ {end})"
        )

    if flow.empty:
        raise ValueError(
            f"No flow data for {ticker} "
            f"({start} ~ {end})"
        )


    # -------------------------
    # Normalize Date
    # -------------------------

    if "Date" not in price.columns:
        price = price.reset_index()

    price["Date"] = pd.to_datetime(price["Date"])
    flow["Date"] = pd.to_datetime(flow["Date"])

    # -------------------------
    # Debug
    # -------------------------

    print(f"Price rows : {len(price)}")
    print(f"Flow rows  : {len(flow)}")

    print(
        f"Price : {price['Date'].min()} ~ {price['Date'].max()}"
    )

    print(
        f"Flow  : {flow['Date'].min()} ~ {flow['Date'].max()}"
    )

    # -------------------------
    # Merge
    # -------------------------

    df = pd.merge(
        price,
        flow,
        on="Date",
        how="inner",
    )

    # -------------------------
    # Remove duplicated columns
    # -------------------------

    duplicates = [
        "Close_y",
        "Volume_y",
    ]

    for col in duplicates:
        if col in df.columns:
            df = df.drop(columns=col)

    df = df.rename(
        columns={
            "Close_x": "Close",
            "Volume_x": "Volume",
        }
    )

    # -------------------------
    # Finalize
    # -------------------------

    df = (
        df.sort_values("Date")
          .drop_duplicates("Date")
          .reset_index(drop=True)
    )

    return df
