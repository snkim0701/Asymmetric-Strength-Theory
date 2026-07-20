"""
Asymmetric Strength Theory
Module : Price Loader
"""

from __future__ import annotations

import pandas as pd
import FinanceDataReader as fdr


def load_price(
    ticker: str,
    start: str,
    end: str,
) -> pd.DataFrame:
    """
    Load price data from FinanceDataReader.
    """

    try:

        df = fdr.DataReader(
            ticker,
            start,
            end,
        )

        if df.empty:

            print(f"[Warning] No price data : {ticker}")
            return pd.DataFrame()

        # Date → column
        df = (
            df.reset_index()
              .sort_values("Date")
              .drop_duplicates("Date")
              .reset_index(drop=True)
        )

        # datetime
        df["Date"] = pd.to_datetime(df["Date"])

        return df

    except Exception as e:

        print(f"[Error] {ticker} : {e}")

        return pd.DataFrame()