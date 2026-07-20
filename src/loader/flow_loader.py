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

    # Remove duplicated dates
    df = (
        df.drop_duplicates(subset="Date")
        .sort_values("Date")
        .reset_index(drop=True)
    )        

    # Keep only HDSDM columns
    columns = [
        "Date",
        "Institution",
        "Foreign",
        "ForeignShares",
        "ForeignRatio",
    ]

    df = df[columns]

    return df

# =========================================================
# Public API
# =========================================================

def load_flow(
        ticker: str,
        start: str | None = None,
        end: str | None = None,
        max_pages=40,
    ):


    df = get_data_parallel(
        ticker,
        max_pages=max_pages
    )

    if df.empty:
        return pd.DataFrame(
            columns=[
                "Date",
                "Institution",
                "Foreign",
                "ForeignShares",
                "ForeignRatio",
            ]
        )
    


    df = clean_flow(df)

    print("=" * 60)
    print("Flow BEFORE date filter")
    print(f"Rows : {len(df)}")
    print(f"Min  : {df['Date'].min()}")
    print(f"Max  : {df['Date'].max()}")


    if start is not None:
        df = df[df["Date"] >= pd.to_datetime(start)]

    if end is not None:
        df = df[df["Date"] <= pd.to_datetime(end)]
    print("=" * 60)
    print("Flow AFTER date filter")
    print(f"Rows : {len(df)}")

    if not df.empty:
        print(f"Min  : {df['Date'].min()}")
        print(f"Max  : {df['Date'].max()}")


    df = (
        df.drop_duplicates(subset="Date")
        .sort_values("Date")
        .reset_index(drop=True)
    )


    return df