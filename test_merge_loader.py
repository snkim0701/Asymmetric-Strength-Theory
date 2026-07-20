from src.loader.merge_loader import load_dataset

def main():
    print("test_merge_loader.py started")
    ticker = "005930"
    start = "2024-01-01"
    end = "2025-12-31"

    df = load_dataset(
        ticker=ticker,
        start=start,
        end=end,
    )

    print("=" * 70)
    print("Dataset Summary")
    print("=" * 70)

    print(f"Ticker : {ticker}")
    print(f"Rows   : {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print()

    print(df.head(3))
    print("...")
    print(df.tail(3))

print("__name__ =", __name__)
if __name__ == "__main__":
    main()
 