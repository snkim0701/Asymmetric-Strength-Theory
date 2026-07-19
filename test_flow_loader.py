from src.loader.flow_loader import load_flow

df = load_flow(
    "005930",
    max_pages=5
)

print(df.head())

print()

print(df.dtypes)

print()

print(df.columns)