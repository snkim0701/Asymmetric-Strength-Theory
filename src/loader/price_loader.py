"""
Asymmetric Strength Theory
Module : Price Loader

Author : Seungnam Kim
Version : 1.1
"""

import FinanceDataReader as fdr


def load_price(ticker, start, end):
    """
    Load price data from FinanceDataReader

    Parameters
    ----------
    ticker : str
        Stock ticker (e.g. '005930')

    start : str
        Start date (YYYY-MM-DD)

    end : str
        End date (YYYY-MM-DD)

    Returns
    -------
    pandas.DataFrame
    """

    df = fdr.DataReader(
        ticker,
        start,
        end
    )

    return df