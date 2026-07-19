from config.ticker_dict import WATCHLIST

print("=" * 50)
print("WATCHLIST")
print("=" * 50)

for ticker, info in WATCHLIST.items():

    print(f"{ticker:8s}  {info['name']:12s}  {info['sector']}")