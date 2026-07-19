"""
flow_loader.py

HDSDM V1.3
Load Foreign / Institution Trading Data
from NAVER Finance
"""

import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor


# =========================================================
# Column Mapping
# =========================================================

COLUMN_MAP = {
    "날짜": "Date",
    "종가": "Close",
    "전일비": "Change",
    "등락률": "Return",
    "거래량": "Volume",
    "기관": "Institution",
    "외국인": "Foreign",
    "외국인.1": "ForeignShares",
    "외국인.2": "ForeignRatio",
}


# =========================================================
# Download one page
# =========================================================

def fetch_page(code, page, headers):

    url = f"https://finance.naver.com/item/frgn.nhn?code={code}&page={page}"

    try:

        res = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        res.encoding = "euc-kr"

        tables = pd.read_html(
            res.text,
            header=0
        )

        for df in tables:

            if (
                "기관" in df.columns
                and "외국인" in df.columns
                and "종가" in df.columns
            ):
                return df.dropna()

    except Exception:
        return None

    return None


# =========================================================
# Parallel Download
# =========================================================

def get_data_parallel(
        code,
        max_pages=5
):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    results = []

    with ThreadPoolExecutor(max_workers=3) as executor:

        futures = [

            executor.submit(
                fetch_page,
                code,
                page,
                headers
            )

            for page in range(1, max_pages + 1)

        ]

        for future in futures:

            df = future.result()

            if df is not None and not df.empty:
                results.append(df)

    if len(results) == 0:
        return pd.DataFrame()

    df = pd.concat(
        results,
        ignore_index=True
    )

    return df


# =========================================================
# Validate Columns
# =========================================================

def validate_columns(df):

    required = [

        "날짜",
        "종가",
        "거래량",
        "기관",
        "외국인",

    ]

    missing = [
        c
        for c in required
        if c not in df.columns
    ]

    if missing:

        raise ValueError(
            f"Missing columns : {missing}"
        )


# =========================================================
# Convert string -> numeric
# =========================================================

def to_number(series):

    s = (
        series.astype(str)
              .str.replace(",", "", regex=False)
              .str.replace("%", "", regex=False)
              .str.strip()
    )

    return pd.to_numeric(
        s,
        errors="coerce"
    )


# =========================================================
# Clean Data
# =========================================================

def clean_flow(df):

    validate_columns(df)

    # Rename columns
    df = df.rename(columns=COLUMN_MAP)

    # Date
    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    # Numeric Columns
    numeric_cols = [

        "Close",
        "Return",
        "Volume",
        "Institution",
        "Foreign",
        "ForeignShares",
        "ForeignRatio",

    ]

    for col in numeric_cols:

        if col in df.columns:

            df[col] = to_number(df[col])

    # Remove invalid dates
    df = df.dropna(
        subset=["Date"]
    )

    # Sort
    df = (
        df.sort_values("Date")
          .reset_index(drop=True)
    )

    # Remove unnecessary column
    df = df.drop(
        columns=["Change"],
        errors="ignore"
    )

    # Integer columns
    int_cols = [

        "Close",
        "Volume",
        "Institution",
        "Foreign",
        "ForeignShares",

    ]

    for col in int_cols:

        if col in df.columns:

            df[col] = df[col].astype("Int64")

    return df


# =========================================================
# Public API
# =========================================================

def load_flow(
        ticker,
        max_pages=5
):

    df = get_data_parallel(
        ticker,
        max_pages=max_pages
    )

    if df.empty:
        return df

    df = clean_flow(df)

    return df